# signata-risk-api

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg)](https://www.digitalocean.com/?refcode=7802e11be119&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)

The Risk API is a python flask service using [Supabase](supabase.com) for record retrieval and storage. It can be easily deployed on services like [DigitalOcean](https://m.do.co/c/7802e11be119) with the following environment variables set:

`SUPABASE_URL`

`SUPABASE_KEY`

## Documentation

[Documentation is hosted on readthedocs](https://docs.signata.net/en/latest/risk.html).

## Development

Set the supabase URL and Key (server key, not client key) for your development environment. For Windows PowerShell:

$Env:SUPABASE_URL = "..."
$Env:SUPABASE_KEY = "..."

VSCode can run the application in debug mode using it's built-in flask debugger.

To call the API, just use an app like Postman to hit http://localhost:5000
