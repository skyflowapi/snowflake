# Snowflake Detokenization Performance Benchmarking

  

This python script does the following:

1. Creates a Skyflow Vault

2. Sets a detokenization limit for the newly created vault

3. Adds data to the vault using the _Faker_ package 

4. Creates a Snowflake database and table

5. Uses the response from the record insertion to add the tokens to the Snowflake table

6. Creates a Snowflake external function that can perform detokenization

7. Benchmarks the `average latency` of the external function for detokenizing each column in the Skyflow Vault

The predetermined schema for the newly created vault is:

```
TokenFormat_DETERMINISTIC_UUID TokenFormat = 1 - first_name

TokenFormat_NON_DETERMINISTIC_UUID TokenFormat = 2 - last_name

TokenFormat_DETERMINISTIC_FPT TokenFormat = 3 - email_id

TokenFormat_NON_DETERMINISTIC_FPT TokenFormat = 4 - ssn

TokenFormat_DETERMINISTIC_PRESERVE_LEFT_6_RIGHT_4 TokenFormat = 5 - card_number
```

To run this script:

##### Create-Vault-and-Insert-Records
```
python3 __main__.py Create-Vault-and-Insert-Records --credentialsFilePath /Users/filepath/credentials.json --createVaultURL https://manage.skyflowapis.dev/v1/vaults --skyflowAccountID abc123 --workspaceID abc123 --numberOfRecordsToBeInserted 1000 —insertURL https://sb.area51.vault.skyflowapis.dev/v1/vaults/
```
##### Detokenize-Limit
```
python3 __main__.py Detokenize-Limit --credentialsFilePath /Users/filepath/credentials.json --detokenizeLimit 100 --detokenizeLimitBaseURL https://sb.area51.vault.skyflowapis.dev/v1/internal/vaults/ --vaultID abc123
```

##### Create Service Account 
```
python3 __main__.py Create-SA --credentialsFilePath /Users/filepath/credentials.json --createSAURL https://manage.skyflowapis.dev/v1/serviceAccounts --secretName SecretName123 --region us-east-2 --awsAccessKeyID ABC123 --awsSecretAccessKey ABC123 --awsSessionToken XYZ456
```

##### Insert-Snowflake
```
python3 __main__.py Insert-Snowflake --snowflakeUser abc123 --snowflakePassword 'password' --snowflakeAccount abc123.prod123456.us-west-2.aws --databaseName DetokenizationTesting --tableName snowflake_benchmarking
```

##### Benchmarking
```
python3 __main__.py Benchmarking --snowflakeUser abc123 --snowflakePassword 'password' --snowflakeAccount abc123.prod123456.us-west-2.aws --databaseName DetokenizationTesting --tableName snowflake_benchmarking --apiIntegrationName abc123 --invocationURL https://invocationURL/
```

The default values of `detokenizeLimit` and `numberOfRecordsToBeInserted` have been set as:
```
detokenizeLimit = 100
numberOfRecordsToBeInserted = 1000
```