import requests # type: ignore warning
from requests.auth import HTTPBasicAuth # type: ignore
import json
from datetime import datetime, timedelta, timezone
API_SECRET = 'MIXPANEL_SECRET'
event_names = [
    "Enable Bill Pay", 
    "Bill Pay Paid", 
    "Enable Zeni Accounts", 
    "Onboarding Link A Bank Account Success",
    "Deposit Accounts Transfer Created"
]
from_date = "2017-01-01"
to_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
domain = "twin.vc" #sobet.io pneumatic.app opensense.com piedpiper.pro terrantic.com 366myrtlebrooklynllc.shop getwiser.io shiloh-events.com supercharge.art piefi.io alliedhds.com hemhealer.com qpilot.cloud thecnctapp.com escapeveloctyentertainment.com bodo.ai siena.cx
url = 'https://data.mixpanel.com/api/2.0/export/'
params = {
    'event': json.dumps(event_names),
    'from_date': from_date,
    'to_date': to_date,
    #'where': f'properties["company_name"] == "Siena AI"' #used to retrieve the Deposit Accounts Transfer Created
    'where': f'properties["tenant_email_domain"] == "{domain}"'
    #'where': f'properties["user_email_domain"] == "{domain}"'
}
response = requests.get(url, auth=HTTPBasicAuth(API_SECRET, ''), params=params)
if response.status_code == 200:
    if response.text:
        events = response.text.splitlines()
        event_data = {event_name: [] for event_name in event_names}
        for event in events:
            event_data_json = json.loads(event)
            event_name = event_data_json['event']
            if event_name in event_data:
                event_data[event_name].append(event_data_json['properties'])
        eventcounts = {}
        enable_bill_payhubspot_datetime = 0
        enable_zeni_accounthubspot_datetime = 0
        recent_onboarding_bank_timestamp = 0
        for name, properties_list in event_data.items():
            properties_list.sort(key=lambda x: x.get('time', 0))
            event_count = len(properties_list)
            eventcounts[name] = event_count 
            if name == "Enable Bill Pay" and properties_list:
                first_timestamp = properties_list[0].get('time')
                if first_timestamp:
                    first_event_datetime = datetime.fromtimestamp(first_timestamp, tz=timezone.utc)
                    enable_bill_payhubspot_datetime = first_event_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            if name == "Enable Zeni Accounts" and properties_list:
                first_timestamp = properties_list[0].get('time')
                if first_timestamp:
                    first_event_datetime = datetime.fromtimestamp(first_timestamp, tz=timezone.utc)
                    enable_zeni_accounthubspot_datetime = first_event_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            if name == "Onboarding Link A Bank Account Success" and properties_list:
                last_timestamp = properties_list[-1].get('time')
                if last_timestamp:
                    recent_event_datetime = datetime.fromtimestamp(last_timestamp, tz=timezone.utc)
                    recent_onboarding_bank_timestamp = recent_event_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f"Earliest timestamp for 'Enable Bill Pay': {enable_bill_payhubspot_datetime}")
        print("Total Number of Bill Pay Paid", eventcounts["Bill Pay Paid"])
        if eventcounts["Bill Pay Paid"] > 0:
            bill_pay_used = True
        else:
            bill_pay_used = False
        print("Bill Pay Used", bill_pay_used)
        print(f"Earliest timestamp for 'Enable Zeni Accounts': {enable_zeni_accounthubspot_datetime}")
        if enable_zeni_accounthubspot_datetime != 0:
            today = datetime.now(timezone.utc)
            zeni_account_days_since = (today - first_event_datetime).days
        else:
            zeni_account_days_since = 0
        print("Days since Accounting Opening", zeni_account_days_since)
        print("Most recent timestamp for Onboarding Link A Bank Account Success", recent_onboarding_bank_timestamp)
        if recent_onboarding_bank_timestamp != 0:
            connection_status_external_account = "Connected"
            today = datetime.now(timezone.utc)
            days_since_last_connected_account = (today - recent_event_datetime).days
        else:
            connection_status_external_account = "Not Connected"
            days_since_last_connected_account = 0
        print("Number of Days since the last connected account", days_since_last_connected_account)
        print("Connection status with external account ", connection_status_external_account)
        print("Total Number of Deposit Accounts Transfer Created", eventcounts["Deposit Accounts Transfer Created"])
    else:
        print("No events found.")
else:
    print(f"Failed to fetch events: {response.status_code}, {response.text}")