from faker import Faker
from skyflow.errors import SkyflowError
import csv
import json
import requests

CSV_FILE = 'snowflake_benchmark_testing.csv'

# insert_records_vault inserts records into the newly created vault


def insert_records_vault(bearerToken, accountID, insertURL, vaultID, numberOfRecordsToBeInserted):

    url = insertURL+vaultID+"/shoppers"

    # Create and initialize a Faker Generator
    fake = Faker()

    try:
        with open(CSV_FILE, 'w', encoding='UTF8', newline='') as file:
            writer = csv.writer(file)
            rec = [[]]

            for i in range(numberOfRecordsToBeInserted):
                first_name = fake.first_name()
                last_name = fake.last_name()

                payload = json.dumps({
                    "quorum": False,
                    "records": [
                        {
                            "fields": {
                                "card_number": fake.credit_card_number(),
                                "email_id": f"{first_name}.{last_name}@{fake.domain_name()}",
                                "first_name": first_name,
                                "last_name": last_name,
                                "ssn": fake.ssn()
                            }
                        }
                    ],
                    "tokenization": True
                })

                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-SKYFLOW-ACCOUNT-ID': accountID,
                    'Authorization': f'Bearer {bearerToken}'
                }
                response = requests.request(
                    "POST", url, headers=headers, data=payload)
                data = response.json()

                inn = [data['records'][0]['tokens']['first_name'], data['records'][0]['tokens']['last_name'], data['records'][0]['tokens']['email_id'],
                       data['records'][0]['tokens']['ssn'], data['records'][0]['tokens']['card_number']]

                rec.append(inn)
            rec.pop(0)
            writer.writerows(rec)
        print("added records to Skyflow Vault")

    except SkyflowError as e:
        print("Error Occurred:", e)
