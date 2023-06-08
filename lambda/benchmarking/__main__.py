from create_vault import create_vault
from set_detokenization_limit import set_detokenize_limit
from insert_records_vault import insert_records_vault
from external_function_snowflake import benchmark, init_external_function
import argparse
from skyflow.service_account import generate_bearer_token, is_expired
from insert_snowflake import insert_snowflake
from create_sa import create_sa
from update_aws_secret import update_aws_secret
import snowflake.connector

parser = argparse.ArgumentParser(
    description="Program Arguments for Benchmarking")

subparsers = parser.add_subparsers(dest='subparser')

parser_1 = subparsers.add_parser(
    'Create-Vault-and-Insert-Records', help='Create Vault')
parser_1.add_argument("--credentialsFilePath", type=str, required=True,
                      help="The path of the credentials.json file downloaded after creating a service account")
parser_1.add_argument(
    "--createVaultURL", type=str, required=True, help="The Create Vault URL")
parser_1.add_argument("--skyflowAccountID", type=str, required=True,
                      help="The Skyflow Account ID where the vault has to be created")
parser_1.add_argument("--workspaceID", type=str, required=True,
                      help="The Workspace ID where the vault has to be created")
parser_1.add_argument("--numberOfRecordsToBeInserted", type=int, default=1000,
                      help="The number of records to be inserted into the newly created vault")
parser_1.add_argument("--insertURL", type=str, required=True,
                      help="The insert vault URL: https://sb.area51.vault.skyflowapis.dev/v1/vaults/")


parser_2 = subparsers.add_parser('Detokenize-Limit', help='Detokenize Limit')
parser_2.add_argument("--credentialsFilePath", type=str, required=True,
                      help="The path of the credentials.json file downloaded after creating a service account")
parser_2.add_argument("--detokenizeLimit", type=int, default=100,
                      help="The maximum detokenize limit for the vault")
parser_2.add_argument("--detokenizeLimitBaseURL", type=str, required=True,
                      help="The base URL to change the detokenize limit of the form: https://sb.area51.vault.skyflowapis.dev/v1/internal/vaults/")
parser_2.add_argument("--vaultID", type=str, required=True,
                      help="The VaultID")

parser_3 = subparsers.add_parser(
    'Create-SA', help='Create SA and Update AWS Secret')
parser_3.add_argument("--credentialsFilePath", type=str, required=True,
                      help="The path of the credentials.json file downloaded after creating a service account")
parser_3.add_argument("--createSAURL", type=str, required=True,
                      help="The Create Service Account URL of the form: https://manage.skyflowapis.dev/v1/serviceAccounts")
parser_3.add_argument("--vaultID", type=str,  required=True,
                      help="The VaultID")
parser_3.add_argument("--secretName", type=str,
                      required=True, help="AWS Secret Name")
parser_3.add_argument("--region", type=str,
                      required=True, help="AWS Region")
parser_3.add_argument(
    "--awsAccessKeyID", required=True, type=str, help="AWS Access Key ID")
parser_3.add_argument("--awsSecretAccessKey", required=True, type=str,
                      help="AWS Secret Access Key")
parser_3.add_argument(
    "--awsSessionToken", type=str, required=True, help="AWS Session Token")


parser_4 = subparsers.add_parser(
    'Insert-Snowflake', help='Insert Tokens into Snowflake')
parser_4.add_argument(
    "--snowflakeUser", type=str, required=True, help="Snowflake user")
parser_4.add_argument(
    "--snowflakePassword", type=str, required=True, help="Snowflake password")
parser_4.add_argument(
    "--snowflakeAccount", type=str, required=True, help="Snowflake account")
parser_4.add_argument(
    "--databaseName", type=str, required=True, help="Snowflake database name")
parser_4.add_argument("--tableName", type=str,
                      required=True, help="Snowflake table name")


parser_5 = subparsers.add_parser('Benchmarking', help='Benchmarking')
parser_5.add_argument(
    "--snowflakeUser", type=str, required=True, help="Snowflake user")
parser_5.add_argument(
    "--snowflakePassword", type=str, required=True, help="Snowflake password")
parser_5.add_argument(
    "--snowflakeAccount", type=str, required=True, help="Snowflake account")
parser_5.add_argument(
    "--databaseName", type=str, required=True, help="Snowflake database name")
parser_5.add_argument("--tableName", type=str,
                      required=True, help="Snowflake table name")
parser_5.add_argument("--apiIntegrationName", type=str, required=True,
                      help="Snowflake API Integration Name")
parser_5.add_argument("--invocationURL", type=str, required=True,
                      help="API Gateway Invocation URL")

args = parser.parse_args()

# Cache for reuse
bearerToken = ''

# token_provider returns generated bearer token


def token_provider():
    global bearerToken
    if not args.credentialsFilePath:
        print("Service account credentials file does not exist in filepath")
    else:
        if is_expired(bearerToken):
            bearerToken, _ = generate_bearer_token(args.credentialsFilePath)
        return bearerToken


# connect_to_snowflake connects to Snowflake
def connect_to_snowflake():

    # Set up the connection parameters
    conn_params = {
        "account": args.snowflakeAccount,
        "user": args.snowflakeUser,
        "password": args.snowflakePassword,

    }
    # Connect to Snowflake
    try:
        conn = snowflake.connector.connect(**conn_params)
    except snowflake.connector.errors.OperationalError as e:
        print(f"Error connecting to Snowflake: {e}")
        exit()

    return conn


def main():

    match args.subparser:

        case 'Create-Vault-and-Insert-Records':
            bearerToken = token_provider()

            vaultID = create_vault(
                args.createVaultURL, args.skyflowAccountID, args.workspaceID, bearerToken)

            insert_records_vault(bearerToken, args.skyflowAccountID, args.insertURL, vaultID,
                                 args.numberOfRecordsToBeInserted)

        case 'Detokenize-Limit':
            bearerToken = token_provider()
            vaultID = args.vaultID

            if args.detokenizeLimit != 100:
                detokenizeLimitURL = args.detokenizeLimitBaseURL+vaultID+"/config"
                set_detokenize_limit(detokenizeLimitURL,
                                     args.detokenizeLimit, bearerToken)

        case 'Create-SA':
            bearerToken = token_provider()

            vaultID = args.vaultID

            output = create_sa(
                args.createSAURL, vaultID, bearerToken)

            update_aws_secret(args.secretName, args.region, args.awsAccessKeyID,
                              args.awsSecretAccessKey, args.awsSessionToken, output)

        case 'Insert-Snowflake':
            conn = connect_to_snowflake()

            insert_snowflake(conn, args.databaseName, args.tableName)

        case 'Benchmarking':
            conn = connect_to_snowflake()

            init_external_function(
                conn, args.databaseName, args.apiIntegrationName, args.invocationURL)

            benchmark(
                conn, args.tableName)

        case _:
            print("Invalid operation")


if __name__ == "__main__":

    main()
