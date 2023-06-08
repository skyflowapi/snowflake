import boto3
from botocore.exceptions import ClientError
import json

# update_aws_secret updates the AWS Secret with the new SA credentials.json values


def update_aws_secret(secretName, region, awsAccessKeyID, awsSecretAccessKey, awsSessionToken, output):

    session = boto3.session.Session(aws_access_key_id=awsAccessKeyID,
                                    aws_secret_access_key=awsSecretAccessKey,
                                    aws_session_token=awsSessionToken)

    try:
        client = session.client(
            service_name='secretsmanager',
            region_name=region,
        )
        client.get_secret_value(SecretId=secretName)

        client.update_secret(
            SecretId=secretName,
            SecretString=json.dumps(output)
        )

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secretName + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print(
                "The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
