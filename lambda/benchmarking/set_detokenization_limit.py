import requests
import json

# set_detokenize_limit sets the detokenize limit for the vault


def set_detokenize_limit(detokenizeLimitURL, detokenizeLimit, bearerToken):

    payload = json.dumps({"VaultMetaConfig": {"vaultConfig": {
                         "MaxDetokenizeSizeLimit": detokenizeLimit}}})
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json', 'Authorization': f'Bearer {bearerToken}'}

    try:
        response = requests.request(
            "POST", detokenizeLimitURL, headers=headers, data=payload)
        response.raise_for_status()
        print("Successfully changed detokenization limit to ", detokenizeLimit)
    except requests.exceptions.HTTPError as error:
        print(f"HTTP error occurred: {error}")
    except requests.exceptions.RequestException as error:
        print(f"An error occurred: {error}")
