import requests

# create_sa creates a Service account for the newly created vault with a Vault Owner role


def create_sa(createSAURL, vaultID, bearerToken):

    try:
        createSAHeaders = {
            "Authorization": f'Bearer {bearerToken}',
            "Content-Type": "application/json"
        }

        createSAbody = {
            "resource": {
                "ID": vaultID,
                "type": "VAULT"
            },
            "serviceAccount": {
                "ID": "",
                "name": "serviceAccount@accountID-skyflow.com",
                "displayName": "SA for Vault Admin",
                "description": "Service account for vault admin"
            },
            "clientConfiguration": {
                "enforceContextID": True,
                "contextIDMapping": "string",
                "enforceSignedDataTokens": True,
                "subjectTokenValidation": True
            }
        }

        response = requests.post(
            createSAURL, headers=createSAHeaders, json=createSAbody)
        response.raise_for_status()

        data = response.json()

        output = {k: v for k, v in data.items() if k in (
            'clientID', 'clientName', 'tokenURI', 'keyID', 'privateKey')}
        print("created service account")
        return output

    except requests.exceptions.HTTPError as error:
        print(f"HTTP error occurred: {error}")

    except requests.exceptions.RequestException as error:
        print(f"An error occurred: {error}")

    except Exception as error:
        print(f"An error occurred: {error}")
