#!/usr/bin/env python3
"""
Check verified caller IDs from Twilio
"""
from twilio.rest import Client
import os

# Load credentials from environment
account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')

client = Client(account_sid, auth_token)

print("Verified Caller IDs:")
print("-" * 50)

try:
    outgoing_caller_ids = client.outgoing_caller_ids.list()

    if not outgoing_caller_ids:
        print("No verified caller IDs found!")

    for caller_id in outgoing_caller_ids:
        print(f"Phone Number: {caller_id.phone_number}")
        print(f"Friendly Name: {caller_id.friendly_name}")
        print(f"SID: {caller_id.sid}")
        print("-" * 50)

except Exception as e:
    print(f"Error: {e}")
