import requests
import json


# create_vault creates a vault and returns the Vault ID
def create_vault(url, accountID, workspaceID, bearerToken):

    headers = {
        'Content-Type': 'application/json',
        'X-SKYFLOW-ACCOUNT-ID': accountID,
        'Authorization': f'Bearer {bearerToken}'
    }

    data = {
        'name': 'Detokenization_Testing_Snowflake_Skyflooow',
        "description": "Benchmarking Snowflake Performance",
        'vaultSchema': {
            "schemas": [{
                "ID": "dd35ebdbb2614ab2b286he60b56yv74",
                "name": "shoppers",
                "fields": [{
                    "name": "skyflow_id",
                    "datatype": 12,
                    "isArray": False,
                    "tags": [{
                        "name": "skyflow.options.default_dlp_policy",
                        "values": ["PLAIN_TEXT"]
                    }, {
                        "name": "skyflow.options.operation",
                        "values": ["ALL_OP"]
                    }, {
                        "name": "skyflow.options.sensitivity",
                        "values": ["LOW"]
                    }, {
                        "name": "skyflow.options.data_type",
                        "values": ["skyflow.SkyflowID"]
                    }, {
                        "name": "skyflow.options.description",
                        "values": ["Skyflow defined Primary Key"]
                    }, {
                        "name": "skyflow.options.display_name",
                        "values": ["Skyflow ID"]
                    }],
                    "properties": None,
                    "index": 0
                }, {
                    "name": "first_name",
                    "datatype": 12,
                    "isArray": False,
                    "tags": [{
                        "name": "skyflow.options.default_dlp_policy",
                        "values": ["MASK"]
                    }, {
                        "name": "skyflow.options.find_pattern",
                        "values": ["(.).*(.{2})"]
                    }, {
                        "name": "skyflow.options.replace_pattern",
                        "values": ["${1}***${2}"]
                    }, {
                        "name": "skyflow.validation.regular_exp",
                        "values": ["^$|^[A-za-z ,.'-;]+$"]
                    }, {
                        "name": "skyflow.options.identifiability",
                        "values": ["MODERATE_IDENTIFIABILITY"]
                    }, {
                        "name": "skyflow.options.operation",
                        "values": ["EXACT_MATCH"]
                    }, {
                        "name": "skyflow.options.default_token_policy",
                        "values": ["DETERMINISTIC_UUID"]
                    }, {
                        "name": "skyflow.options.configuration_tags",
                        "values": ["NULLABLE"]
                    }, {
                        "name": "skyflow.options.personal_information_type",
                        "values": ["PII", "PHI"]
                    }, {
                        "name": "skyflow.options.privacy_law",
                        "values": ["GDPR", "CCPA", "HIPAA"]
                    }, {
                        "name": "skyflow.options.description",
                        "values": ["An individual's first, middle, or last name"]
                    }, {
                        "name": "skyflow.options.display_name",
                        "values": ["first_name"]
                    }],
                    "properties": None,
                    "index": 0
                }, {
                    "name": "last_name",
                    "datatype": 12,
                    "isArray": False,
                    "tags": [{
                        "name": "skyflow.options.default_dlp_policy",
                        "values": ["MASK"]
                    }, {
                        "name": "skyflow.options.find_pattern",
                        "values": ["(.).*(.{2})"]
                    }, {
                        "name": "skyflow.options.replace_pattern",
                        "values": ["${1}***${2}"]
                    }, {
                        "name": "skyflow.validation.regular_exp",
                        "values": ["^$|^[A-za-z ,.'-;]+$"]
                    }, {
                        "name": "skyflow.options.identifiability",
                        "values": ["MODERATE_IDENTIFIABILITY"]
                    }, {
                        "name": "skyflow.options.operation",
                        "values": ["EXACT_MATCH"]
                    }, {
                        "name": "skyflow.options.default_token_policy",
                        "values": ["NON_DETERMINISTIC_UUID"]
                    }, {
                        "name": "skyflow.options.configuration_tags",
                        "values": ["NULLABLE"]
                    }, {
                        "name": "skyflow.options.personal_information_type",
                        "values": ["PII", "PHI"]
                    }, {
                        "name": "skyflow.options.privacy_law",
                        "values": ["GDPR", "CCPA", "HIPAA"]
                    }, {
                        "name": "skyflow.options.description",
                        "values": ["An individual's first, middle, or last name"]
                    }, {
                        "name": "skyflow.options.display_name",
                        "values": ["last_name"]
                    }],
                    "properties": None,
                    "index": 0
                }, {
                    "name": "email_id",
                    "datatype": 12,
                    "isArray": False,
                    "tags": [{
                        "name": "skyflow.options.default_dlp_policy",
                        "values": ["MASK"]
                    }, {
                        "name": "skyflow.options.find_pattern",
                        "values": ["^(.).*?(.)?@(.+)"]
                    }, {
                        "name": "skyflow.options.replace_pattern",
                        "values": ["$1******$2@$3"]
                    }, {
                        "name": "skyflow.validation.regular_exp",
                        "values": ["^$|^([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,})$"]
                    }, {
                        "name": "skyflow.options.identifiability",
                        "values": ["HIGH_IDENTIFIABILITY"]
                    }, {
                        "name": "skyflow.options.operation",
                        "values": ["EXACT_MATCH"]
                    }, {
                        "name": "skyflow.options.default_token_policy",
                        "values": ["DETERMINISTIC_FPT"]
                    }, {
                        "name": "skyflow.options.format_preserving_regex",
                        "values": ["^([a-z]{20})@([a-z]{10})\\.com$"]
                    }, {
                        "name": "skyflow.options.personal_information_type",
                        "values": ["PII", "PHI"]
                    }, {
                        "name": "skyflow.options.privacy_law",
                        "values": ["GDPR", "CCPA", "HIPAA"]
                    }, {
                        "name": "skyflow.options.description",
                        "values": ["An email address"]
                    }, {
                        "name": "skyflow.options.display_name",
                        "values": ["email_id"]
                    }],
                    "properties": None,
                    "index": 0
                }, {
                    "name": "ssn",
                    "datatype": 12,
                    "isArray": False,
                    "tags": [{
                        "name": "skyflow.options.default_dlp_policy",
                        "values": ["MASK"]
                    }, {
                        "name": "skyflow.options.find_pattern",
                        "values": ["^[0-9]{3}([- ])?[0-9]{2}([- ])?([0-9]{4})$"]
                    }, {
                        "name": "skyflow.options.replace_pattern",
                        "values": ["XXX${1}XX${2}${3}"]
                    }, {
                        "name": "skyflow.validation.regular_exp",
                        "values": ["^$|^([0-9]{3}-?[0-9]{2}-?[0-9]{4})$"]
                    }, {
                        "name": "skyflow.options.identifiability",
                        "values": ["HIGH_IDENTIFIABILITY"]
                    }, {
                        "name": "skyflow.options.operation",
                        "values": ["EXACT_MATCH"]
                    }, {
                        "name": "skyflow.options.default_token_policy",
                        "values": ["NON_DETERMINISTIC_FPT"]
                    }, {
                        "name": "skyflow.options.personal_information_type",
                        "values": ["PII", "PHI", "NPI"]
                    }, {
                        "name": "skyflow.options.privacy_law",
                        "values": ["GDPR", "CCPA", "HIPAA"]
                    }, {
                        "name": "skyflow.options.description",
                        "values": ["A United States Social Security number (SSN) is a 9-digit number of format xxx-xx-xxxx issued to US citizens, permanent residents, and temporary residents."]
                    }, {
                        "name": "skyflow.options.display_name",
                        "values": ["ssn"]
                    }],
                    "properties": None,
                    "index": 0
                }, {
                    "name": "card_number",
                    "datatype": 12,
                    "isArray": False,
                    "tags": [{
                        "name": "skyflow.options.default_dlp_policy",
                        "values": ["MASK"]
                    }, {
                        "name": "skyflow.options.find_pattern",
                        "values": ["[0-9 -]*([0-9 -]{4}$)"]
                    }, {
                        "name": "skyflow.options.replace_pattern",
                        "values": ["XXXXXXXXXXXX${1}"]
                    }, {
                        "name": "skyflow.validation.regular_exp",
                        "values": ["^$|^[\\s]*?([0-9]{2,6}[ -]?){3,5}[\\s]*$"]
                    }, {
                        "name": "skyflow.options.identifiability",
                        "values": ["HIGH_IDENTIFIABILITY"]
                    }, {
                        "name": "skyflow.options.operation",
                        "values": ["EXACT_MATCH"]
                    }, {
                        "name": "skyflow.options.default_token_policy",
                        "values": ["DETERMINISTIC_PRESERVE_LEFT_6_RIGHT_4"]
                    }, {
                        "name": "skyflow.options.personal_information_type",
                        "values": ["PII", "PHI", "NPI"]
                    }, {
                        "name": "skyflow.options.privacy_law",
                        "values": ["GDPR", "CCPA", "HIPAA"]
                    }, {
                        "name": "skyflow.options.data_type",
                        "values": ["skyflow.CardNumber"]
                    }, {
                        "name": "skyflow.options.description",
                        "values": ["Credit or debit card number"]
                    }, {
                        "name": "skyflow.options.display_name",
                        "values": ["card_number"]
                    }],
                    "properties": None,
                    "index": 0
                }],
                "childrenSchemas": [],
                "schemaTags": [{
                    "name": "skyflow.options.description",
                    "values": ["Scratch Table is a minimal table in a vault."]
                }, {
                    "name": "skyflow.options.display_name",
                    "values": ["ScratchTable"]
                }],
                "properties": None,

            }],
            "tags": []
        },
        "workspaceID": workspaceID,
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_dict = json.loads(response.text)
        vaultID = response_dict["ID"]
        print("created vault with VaultID ", vaultID)
        return (vaultID)

    except requests.exceptions.HTTPError as error:
        print(f"HTTP error occurred: {error}")

    except requests.exceptions.RequestException as error:
        print(f"An error occurred: {error}")
