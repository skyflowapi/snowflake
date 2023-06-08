# Detokenization Lambda for Snowflake

This Detokenization Lambda permits queries such as `select detokenize(‘12ab7c59-18b2-4db8-8b9f-1135a42ba96a’);` to be run directly from the Snowflake session 

To set up the full workflow please see [this](https://docs.google.com/document/d/10qHaY0RfPB3ZVq77_69VkYhj2nzHZ6OvUOwFx-TZ5ag/edit?usp=sharing)

To deploy this Go Lambda Function:
1. Navigate to the _detokenize_ folder of this project in your terminal and run the following command: 

`GOOS=linux GOARCH=amd64 go build -o main cmd/main.go`

2. Now go one level up using the `cd ..` command 

3. You should now be at the _lambda_ folder of this project. Run the following command:

`zip -r detokenize.zip detokenize/ `

4. This will create a _.zip_ file named _detokenize.zip_
5. Go to your AWS Management Lambda Console and in your _Runtime Settings_ click on _Edit_. Change your _Handler_ to `detokenize/main`
6. Upload the zip file using the _Upload from_ button 
7. You should now be able to test this Lambda by going to the _Test_ tab
8. An example test (add tokens that correspond to entries in the _Vault_ you have used in the setup): 

``{
"body": "{ \"data\": [  [ 0, \"942a4a1d-6b58-4375-9978-df1eea23715f\", \"a5ade527-cf3e-4485-93ee-9a9bd4007f78\" ] , [ 1, \"9f875ec2-70ee-4fea-ab2f-ee130c683cc9\", \"d4542e8b-094f-4eb8-80f5-7e1d0358ff37\" ] ] }"
}``

#### Provisioning steps if you are using AWS CLI:

Please install the AWS CLI from [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). Before these commands 
can be executed, you need to manually set AWS environment variables or use AWS IAM Identity Center Credentials.  


```
aws secretsmanager create-secret \
    --name Detokenize-Lambda \
    --secret-string file://credentials.json
aws iam create-role --role-name Detokenization-lambda --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
aws lambda create-function --function-name detokenize --runtime go1.x --role arn:aws:iam::999999999999:role/Detokenization-lambda --handler detokenize/main --zip-file fileb://detokenize.zip
aws lambda update-function-configuration --function-name detokenize --environment Variables="{SECRET_NAME=Detokenize-Lambda, VAULT_ID=u0f758f7eb164053989c29a07b9b2aef, VAULT_URL=https://sb.area51.vault.skyflowapis.dev, PARAMETERS_SECRETS_EXTENSION_CACHE_ENABLED=true, PARAMETERS_SECRETS_EXTENSION_LOG_LEVEL=debug}"
aws lambda update-function-configuration --function-name detokenize \
--layers arn:aws:lambda:us-east-2:111111111111:layer:AWS-Parameters-and-Secrets-Lambda-Extension:4
aws lambda invoke --function-name detokenize --cli-binary-format raw-in-base64-out --payload '{}' response.json
aws iam attach-role-policy --role-name Detokenization-lambda --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam create-policy --policy-name GetSecretValue --policy-document file://GetSecretValue.json
aws iam attach-role-policy --role-name Detokenization-lambda --policy-arn arn:aws:iam::999999999999:policy/GetSecretValue
aws apigateway create-rest-api --name 'DetokenizationAPI' --endpoint-configuration types='REGIONAL'
aws apigateway get-resources --rest-api-id abcde12345
aws apigateway create-resource --rest-api-id abcde12345 --parent-id fghij67890 --path-part 'detokenization-api-proxy'
aws apigateway put-method --rest-api-id abcde12345 \
--resource-id klm123 \
--http-method POST \
--authorization-type "AWS_IAM"
aws apigateway put-integration --rest-api-id abcde12345 \
--resource-id klm123 \
--http-method POST \
--type AWS \
--integration-http-method POST \
--uri arn:aws:apigateway:us-east-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-2:999999999999:function:detokenize/invocations \
aws apigateway create-deployment --rest-api-id abcde12345 --stage-name 'detokenization-stage'
aws apigateway update-rest-api \
     --rest-api-id abcde12345  \
     --patch-operations op=replace,path=/policy,value=$(jq tostring Resource_Policy.json)
aws apigateway create-api-key --name 'SkyflowAPIKey'  --enabled --stage-keys restApiId='abcde12345',stageName='detokenization-stage'
aws apigateway create-usage-plan --name "SkyflowUsagePlan"  --throttle burstLimit=200,rateLimit=100 --quota limit=500,offset=0,period=MONTH --api-stages apiId=abcde12345,stage=detokenization-stage
aws apigateway --region us-east-2 update-usage-plan --usage-plan-id xyz789 --patch-operations op="replace",path="/apiStages/abcde12345:detokenization-stage/throttle/skyflow-detokenization-proxy/POST/rateLimit",value="100"
aws apigateway --region us-east-2 update-usage-plan --usage-plan-id xyz789 --patch-operations op="replace",path="/apiStages/abcde12345:detokenization-stage/throttle/skyflow-detokenization-proxy/POST/burstLimit",value="200"
aws apigateway create-usage-plan-key --usage-plan-id xyz789 --key-type "API_KEY" --key-id lmno12345  
aws iam update-assume-role-policy --role-name Detokenization-lambda --policy-document file://Trust_Policy.json
```
The `GetSecretValue.json`:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "arn:aws:secretsmanager:us-east-2:999999999999:secret:Detokenize-Lambda-t1znor"
        }
    ]
}
```


The `Resource Policy.json`:

```
{
"Version": "2012-10-17",
"Statement":
[
{
"Effect": "Allow",
"Principal":
{
"AWS": "arn:aws:sts::999999999999:assumed-role/Detokenization-lambda/snowflake"
},
"Action": "execute-api:Invoke",
"Resource": "arn:aws:execute-api:us-east-2:999999999999:abcde12345/*/POST/detokenization-api-proxy"
}
]
}
```

The `Trust_Policy.json` :

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:user/1ab23456-s"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "ABC12345_SFCRole=2_6dvLb0CQk7mvyN1mt31lBrSzch4="
                }
            }
        }
    ]
}
```

Remember to:

1. Edit the `GetSecretValue.json` policy's `Resource` field to include your `Secret ARN` that is present in the response while creating your Secret in the first step

2. Edit the Integration Request page in the API Gateway by selecting the `Use Lambda Proxy integration`

3. Create a template to store the values created during this provisioning process

4. Replace values in the steps above with the values you get in the response, from the management console and from Snowflake during your setup where appropriate

#### Response Translator in Snowflake:

To use a response translator do the following:

1) Go to your Lambda Console and go to the Configuration -> Environment Variables tab and change the value of `ENABLE_RESPONSE_TRANSLATOR` to `true`


2) Go to your Snowflake console and run the following commands. Use the output from the `select count` statement  as `input_count_value` in your function.

```
select count(column_name) from table_name;

CREATE OR REPLACE FUNCTION detokenization_response(EVENT OBJECT)
RETURNS OBJECT
LANGUAGE JAVASCRIPT AS
'
var responses =[];
if (EVENT.body.error!=null){
for(i=0; i<input_count_value;i++){
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

create or replace external function skyflowdetokenization(value string)
    returns variant
    RETURNS NULL ON NULL INPUT
    api_integration = my_api_integration
    response_translator = database_name.schema_name.detokenization_response
    headers = (
     'method'='detokenize')
     MAX_BATCH_ROWS = 100
    as 'https://{invocationURL}'
;
```

This assumes that you have created and described the api integration. 