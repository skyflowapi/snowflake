# Detokenize data in Snowflake

This tutorial explains how to detokenize data from Skyflow vaults within Snowflake. When you're done, you'll be able to write queries like `select detokenize(email);` directly within a Snowflake session.

This process involves several steps, including
- Creating a service account for your vault
- Creating a Lambda function in AWS to proxy/translate requests from Snowflake to Skyflow
- Configuring Snowflake to use the Lambda function as an API endpoint
- Setting up an API integration in Snowflake

## Prerequisites

- A Skyflow vault with data to detokenize
- A `credentials.json` file for a [service account](https://docs.skyflow.com/api-authentication/#create-a-service-account) with detokenization permissions
- A Snowflake account
- An AWS account that can
    - Store secrets in AWS Secrets Manager
    - Create AWS Lambda functions
- A machine that has
    - [Go](https://go.dev/doc/install) 1.x
    - `bash`

## Store your credentials in AWS

You need to create a service account key for your vault and set it up within AWS Secrets Manager to be used by the Lambda function.

1.  In AWS Secrets Manager, click **Store a new secret**.
2.  Choose **Other type of secret**.
3.  Click **Plaintext**.
4.  Open your `credentials.json` file and copy its contents into the **Plaintext** field.
5.  Click **Next**.
6.  For **Secret name**, enter "skyflow_detokenize".
7.  Finish creating the secret with your typical settings.
8.  Note the **Secret name** and **Secret ARN** values. You'll need them later.

## Create the Lambda function

Next, you'll create and configure the Lambda function to detokenize values from your vault.

1.  Prepare the code:
    1.  If you haven't already done so, clone the Snowflake Detokenization repo and navigate into it:

        ```bash
        git clone https://github.com/skyflowapi/snowflake
        cd snowflake
        ```
    2.  In your terminal, navigate to the `lambda/detokenize` folder and build the lambda function:

        - macOS/Linux:

          ```bash
          cd lambda/detokenize
          GOOS=linux GOARCH=amd64 go build -o main cmd/main.go
          cd ..
          zip -r detokenize.zip detokenize/
          ```

        - Windows:

          ```cmd
          cd lambda\detokenize
          go.exe install github.com/aws/aws-lambda-go/cmd/build-lambda-zip@latest
          set GOOS=linux
          set GOARCH=amd64
          set CGO_ENABLED=0
          go build main.go
          %USERPROFILE%\Go\bin\build-lambda-zip.exe -o detokenize.zip main
          ```

        This creates a `detokenize.zip` file. You'll need this later.

2.  Create the Lambda:
    1.  In AWS Lambda, click **Create function**.
    2.  For **Function name**, enter "detokenize_in_snowflake".
    3.  For **Runtime**, choose **Go 1.x**.
    4.  For **Architecture**, choose **x86_64**.
    5.  Click **Create**.
3.  Under **Code source**, click **Upload from**, choose **.zip file**, and upload the `detokenize.zip` file you created earlier.
4.  Configure the runtime settings:
    1.  Under **Runtime settings**, click **Edit**.
    2.  Set **Handler** to "detokenize/main", then click **Save**.
5.  Configure the layers:
    1.  Under **Layers**, click **Add a layer**.
    2.  For **Layer source**, choose **AWS layers**.
    3.  For **AWS layers**, choose **AWS-Parameters-and-Secrets-Lambda-Extension**.
    4.  For **Version**, choose **4**, then click **Add**.
6.  Configure environment variables:
    1.  Click the **Configuration** tab, then click **Environment variables**.
    2.  Create and set the following variables as key-value pairs:

| Key                                          | Value                                                     |
| -------------------------------------------- | --------------------------------------------------------- |
| `SECRET_NAME`                                | The name of the secret you created.                       |
| `VAULT_ID`                                   | Your Skyflow Vault ID. Found on your Vault Details page.  |
| `VAULT_URL`                                  | Your Skyflow Vault URL. Found on your Vault Details page. |
| `PARAMETERS_SECRETS_EXTENSION_CACHE_ENABLED` | `true`                                                    |
| `PARAMETERS_SECRETS_EXTENSION_LOG_LEVEL`     | `debug`                                                   |
| `ENABLE_RESPONSE_TRANSLATOR`                 | `false`. Can be `true` if needed.                         |

7.  Configure permissions:
    1.  Click **Permissions**, then click the Execution role name. This opens a new IAM tab.
    2.  In the IAM tab, under **Permissions**, click **Add permissions** > **Attach policies**.
    3.  Click **Create policy**. This opens another new tab.
    4.  For **Policy editor**, choose **JSON**, then paste the following policy. Replace `[SECRET_ARN]` with the ARN for the **skyflow_detokenize** secret you created earlier.

        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": "secretsmanager:GetSecretValue",
                    "Resource": "[SECRET_ARN]"
                }
            ]
        }
        ```

    5.  Click **Next**.
    6.  For **Policy name**, enter "GetSecretValue".
    7.  Click **Create policy**.
    8.  Close this IAM tab.
    9.  In the remaining IAM tab, click the **Refresh** button.
    10. Search for "GetSecretValue", check the box next to the matching policy, then click **Add permissions**.
    11. Close the IAM tab.

## Create the Snowflake role

For Snowflake to interact with the Lambda function, you need to create a role for Snowflake.

1.  In AWS IAM, click **Roles**, then click **Create role**.
2.  For **Trusted entity type**, choose **AWS account**.
3.  Under **An AWS account**, either
    - choose **This account**.
    - choose **Another AWS account**, then enter the account ID for the account you want to access this role.
4.  Note the account ID you use for this role. You'll need it later.
5.  Click **Next**, then click **Next** again without modifying or adding any permissions.
6.  For **Role name**, enter "snowflake_role".
7.  Click **Create role**.
8.  From the list of roles, click the role you just created.
9.  Note the **ARN** value. You'll need it later.

## Create the API Gateway

Creating an API Gateway gives Snowflake a way to access the Lambda function.

1.  In AWS API Gateway, click **Create API**.
2.  Under **REST API**, click **Build**.
3.  Under **Create new API**, choose **New API**.
4.  For **API name**, enter "detokenization_in_snowflake".
5.  For **Endpoint Type**, choose "Regional".
6.  Click **Create API**.
7.  Create the "detokenize" resource:
    1.  In the **Resources** section, click **Actions** > **Create Resource**.
    2.  For **Resource name**, enter "detokenize".
    3.  For **Resource path**, enter "detokenize".
    4.  Click **Create Resource**.
8.  Create the "POST" method:
    1.  Click **Actions** > **Create Method**.
    2.  For the HTTP method, choose **POST**, then click the checkmark.
    3.  Check **Use Lambda Proxy integration**.
    4.  For **Lambda Function**, enter "detokenize_in_snowflake".
    5.  Click **Save**. If you get a warning, click **OK**.
9.  Deploy the API:
    1.  Click **Actions** > **Deploy API**.
    2.  For **Deployment stage**, choose **New Stage**.
    3.  For **Stage name**, enter a value.
    4.  Click **Deploy**.
10. In the **Stages** section, click the stage you just created, and continue expanding elements until you see **POST** under "detokenize".
11. Click **POST**, then note the **Invoke URL** value. You'll need it later.

    **Note:** Make sure that the URL includes "detokenize". If it doesn't, you may have clicked on the invocation URL for the stage rather than the "detokenize" resource.

## Restrict access to the API Gateway

Now you need to secure the AWS API Gateway so that only your Snowflake account can access it.

1.  Configuration authorization:
    1.  In the left navigation, click **Resources**.
    2.  In the **Resources** section under **/detokenize**, click **POST**.
    3.  Click **Method Request**.
    4.  For **Authorization**, click the pencil button, choose **AWS_IAM**, and click the check button.
    5.  Click **Method execution** to go back.
    6.  Under **Method Request**, note the **ARN** value. You'll need it later.
2.  Set a resource policy:
    1.  In the left navigation, click **Resource Policy**.
    2.  Update the following policy according to the table, then paste the policy into the **Resource Policy** field.

        ```json
        {
            "Version": "2012-10-17",
            "Statement":
            [
                {
                "Effect": "Allow",
                "Principal":
                    {
                    "AWS": "arn:aws:sts::[ACCOUNT_ID]:assumed-role/[ROLE_NAME]/snowflake"
                    },
                "Action": "execute-api:Invoke",
                "Resource": "[METHOD_REQUEST_ARN]"
                }
            ]
        }
        ```

| Placeholder            | Value                                                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `[ACCOUNT_ID]`         | The 12-digit AWS account ID associated with "snowflake_role".                                                          |
| `[ROLE_NAME]`          | "snowflake_role", or whatever value you entered for the name in [Create a Snowflake role](#create-the-snowflake-role). |
| `[METHOD_REQUEST_ARN]` | Your Method Request ARN.                                                                                               |

    3.  Click **Save**.

3.  Redeploy the API:
    1.  In the left navigation, click **Resources**.
    2.  Click **Actions** > **Deploy API**.
    3.  For **Deployment stage**, choose the stage you created earlier.
    4.  Click **Deploy**.

4.  Set up API keys:
    1.  In the left navigation, click **Resources**.
    2.  In the **Resources** section under **/detokenize**, click **POST**.
    3.  Click **Method Request**.
    4.  For **API Key Required**, click the pencil button, choose **true**, and click the check button.
    5.  In the left navigation, click **API Keys**.
    6.  Click **Actions** > **Create API key**.
    7.  For **Name**, enter "Snowflake Key", then click **Save**.
    8.  Next to **API key**, click **Show**.
    9.  Note the API key value. You'll need it later.

5.  Create a usage plan:
    1.  In the left navigation, click **APIs**, then find and click **detokenization_in_snowflake**.
    2.  In the left navigation, click **Usage Plans**, then click **Create**.
    3.  For **Name**, enter "Snowflake Usage Plan".
    4.  For **Rate**, enter "200".
    5.  For **Burst**, enter "300".
    6.  For **Quota**, enter "150,000,000".
    7.  Click **Next**.
    8.  Click **Add API Stage**.
    9.  For **API**, choose **detokenization_in_snowflake**.
    10. For **Stage**, choose the stage you created earlier, then click the check button.
    11. Click **Configure Method Throttling**, then click **Add Resource/Method**.
    12. For **Resource**, choose **/detokenize**.
    13. For **Method**, choose **POST**.
    14. For **Rate**, enter "200".
    15. For **Burst**, enter "300".
    16. Click the check button, then click **Close**.
    17. Click **Next**.
    18. Click **Add API Key to Usage Plan**.
    19. For **Name**, enter "Snowflake Key", choose the option that appears, then click the check button.
    20. Click **Done**.

## Create an API integration in Snowflake

Now you need to create an API integration in Snowflake that uses the API Gateway you just created.

1.  In Snowflake, open a console with `ACCOUNTADMIN` privileges or a role with the `CREATE INTEGRATION` privilege.
2.  To create an API integration, run the following command, replacing placeholder values according to the table:

    ```sql
    create or replace API INTEGRATION detokenize_api_integration
      API_PROVIDER = AWS_API_GATEWAY
      API_KEY = '[API_KEY]'
      API_AWS_ROLE_ARN = '[ROLE_ARN]'
      API_ALLOWED_PREFIXES = ('[INVOCATION_URL]')
      ENABLED = TRUE;
    ;
    ```

| Placeholder        | Value                                 |
| ------------------ | ------------------------------------- |
| `[API_KEY]`        | The "snowflake_key" API key.          |
| `[ROLE_ARN]`       | The "snowflake_role" ARN.             |
| `[INVOCATION_URL]` | The invocation URL you noted earlier. |

1.  To verify the information was created properly and get additional information, run the following command:

    ```sql
    describe integration detokenize_api_integration
    ```

1.  Note the following values:

    - Find the "API_AWS_IAM_USER_ARN" property and note its "property_value".
    - Find the "API_AWS_EXTERNAL_ID" property and note its "property_value". This value often ends with an equal sign ("="). That is expected and should be included in the value you note.

## Set up a trust relationship between Snowflake and the IAM role

1.  In AWS IAM, click **Roles**.
2.  Find the click "snowflake_role".
3.  Click the **Trust relationships** tab, the click **Edit trust policy**.
4.  Update the following policy according to the table, then paste the policy into the **Edit trust policy** field:

    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "AWS": "[API_AWS_IAM_USER_ARN]"
          },
          "Action": "sts:AssumeRole",
          "Condition": { "StringEquals": { "sts:ExternalId": "[API_AWS_EXTERNAL_ID]" } }
        }
      ]
    }
    ```

| Placeholder              | Value                                               |
| ------------------------ | --------------------------------------------------- |
| `[API_AWS_IAM_USER_ARN]` | The API_AWS_IAM_USER_ARN from your API integration. |
| `[API_AWS_EXTERNAL_ID]`  | The API_AWS_EXTERNAL_ID from your API integration.  |

5.  Click **Update policy**.

## Create a response translator

Now you can create your response translator in Snowflake.

1.  Open a Snowflake console.
2.  To create a response translator, run the following command, replacing placeholder values according to the table:

    ```sql
    select count([COLUMN_NAME]) from [TABLE_NAME];
    ```

| Placeholder     | Value                                                                   |
| --------------- | ----------------------------------------------------------------------- |
| `[COLUMN_NAME]` | The name of the column you want to detokenize in your Skyflow vault.    |
 | `[TABLE_NAME]`  | The name of the table that the column belongs to in your Skyflow vault. |

3.  Replacing [INPUT_COUNT_VALUE] with the result of the query, run the following command:

    ```sql
    CREATE OR REPLACE FUNCTION detokenization_response(EVENT OBJECT)
    RETURNS OBJECT
    LANGUAGE JAVASCRIPT AS
    '
    var responses =[];
    if (EVENT.body.error!=null){
    for(i=0; i<[INPUT_COUNT_VALUE];i++){
    if (i==0){
    let result=[i, EVENT.body]
    responses[i] = result
    }
    else{
    let result = [i,null]
    responses[i] = result
    }
    }
    return { "body": { "data" :responses } };
    }
    else{
    return { "body": EVENT.body };
    }
    ';
    ```

## Create the external function

Now you're ready to create an external function in Snowflake.

In a Snowflake console, run the following command, replacing placeholder values according to the table:

```sql
create or replace external function detokenize(value string)
    returns variant
    RETURNS NULL ON NULL INPUT
    API_INTEGRATION = detokenize_api_integration
    RESPONSE_TRANSLATOR = [DATABASE_NAME].[SCHEMA_NAME].detokenization_response
    HEADERS = (
    'method'='detokenize')
    MAX_BATCH_ROWS = 100
    AS '[INVOCATION_URL]'
;
```

| Placeholder        | Value                                                           |
| ------------------ | --------------------------------------------------------------- |
| `[DATABASE_NAME]`  | The name of the database that contains the response translator. |
| `[SCHEMA_NAME]`    | The name of the schema that contains the response translator.   |
| `[INVOCATION_URL]` | The invocation URL you noted earlier.                           |


You can now call the `detokenize` external function!

```sql
SELECT detokenize('d2037178-646f-42c9-b73e-c3edf10d9805');

SELECT detokenize(column_name), column_name from table_name;
```
