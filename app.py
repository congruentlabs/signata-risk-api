from datetime import datetime, timedelta
from functools import wraps
import os
from flask import Flask
from flask import request, abort
from eth_utils import is_address
from supabase import create_client, Client
import supabase

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

app = Flask(__name__)


def get_api_key(key):
    """
    Searches for a given API Key from the db
    @param key: API Key to search the db for
    @return: Record if found, None if not found
    """
    api_key_records = supabase.table("api_keys").select("*").eq('api_key', key).execute()
    if len(api_key_records.data) == 0:
        return None
    else:
        return api_key_records.data[0]


def validate_api_key(key, type):
    """
    Validates a given API Key
    @param key: API Key from Request
    @return: boolean
    """
    if key is None:
        return False
    api_key = get_api_key(key)
    if api_key is None:
        return False
    elif api_key["api_key"] == key and api_key["type"] == type:
        return True
    return False


def require_write_key(f):
    """
    @param f: Flask function
    @return: decorator
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if validate_api_key(request.headers.get('X-Api-Key'), 'write'):
            return f(*args, **kwargs)
        else:
            abort(401)
        return decorated


def require_read_key(f):
    """
    @param f: Flask function
    @return: decorator
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if validate_api_key(request.headers.get('X-Api-Key'), 'read'):
            return f(*args, **kwargs)
        else:
            abort(401)
        return decorated


@app.route("/")
def get_version():
    return "0.0.1"


def update_risk_level(addr):
    return False


@app.route("/api/v1/riskLevel/<addr>", methods=['GET'])
@require_read_key
def get_risk_level(addr):
    """
    @param addr: Address to check risk level of
    @return: string of risk level
    """
    # simple address validation
    if not is_address(addr):
        return 'Invalid Address', 400

    current_risk_data = supabase.table("risk_data").select("*").eq('address', addr).execute()

    if len(current_risk_data.data) == 0:
        # if there's no record, query the event data to see if a value can be generated
        current_event_data = supabase.table("risk_events").select("*").eq('address', addr).execute()
        
        if len(current_event_data.data) == 0:
            # set it as unknown (0), write it to the risk_data table
            supabase.table('risk_data').insert({"address": addr, "risk_level": 0}).execute()
            # return the same unknown value
            return '0'
        else:
            # force an update
            update_risk_level(addr)
            return '0'
    else:
        risk_data_record = current_risk_data.data[0]
        updated_at = datetime.strptime(risk_data_record['updated_at'], "%Y-%m-%dT%H:%M:%S.%f+00:00")

        if updated_at > datetime.now() - timedelta(hours=6):
            # force an update
            # update_risk_level(addr)
            return str(risk_data_record['risk_level'])
        else:
            return str(risk_data_record['risk_level'])


@app.route("/api/v1/riskEvents", methods=['POST'])
@require_write_key
def add_risk_event():
    """
    Injects a risk event from the JSON request body.
    Requires a 'write' X-Api-Key
    @return: 200 OK
    """
    data = request.json

    if not is_address(data.address):
        return 'Invalid Address', 400

    supabase.table('risk_events').insert({
        "address": data.address,
        "device_thumbprint": data.device_thumbprint,
        "geolocation_thumbprint": data.geolocation_thumbprint,
        "access_type": data.access_type,
        "reported_by": data.reported_by
        }).execute()

    return 'Event Added', 200
