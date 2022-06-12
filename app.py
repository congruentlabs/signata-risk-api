from datetime import datetime, timedelta
import os
from flask import Flask
from flask import request
from eth_utils import is_address
from supabase import create_client, Client
import supabase

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

app = Flask(__name__)

@app.route("/")
def get_version():
    return "0.0.1"

def update_risk_level(addr):
    return False

@app.route("/api/v1/riskLevel/<addr>", methods=['GET'])
def get_risk_level(addr):
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
def add_risk_event():
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
