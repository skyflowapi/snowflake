# Snowflake Commands

These commands must be run in your Snowflake console. 

1) To create your api integration

```
create or replace api integration my_aws_api_integration
  api_provider = aws_api_gateway
  API_KEY = '<API_Key>'
  api_aws_role_arn = '<new_IAM_role_ARN >'
  api_allowed_prefixes = ('https://{invocation url}')
  enabled = true
;

```
2) To describe your api integration

```
describe integration my_aws_api_integration;

```

3) To create and use your response translator. Use the output from the `select count` statement  as `input_count_value` in your function.

```

use database your_database_name;

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

```

4) To create your external function 

```
create or replace external function detokenize(value string)
    returns variant
    RETURNS NULL ON NULL INPUT
    api_integration = <your_api_integration_name>
    response_translator = <database_name.schema_name.detokenization_response> 
    headers = (
     'method'='detokenize')
     MAX_BATCH_ROWS = 100
    as 'https://{invocation url}'
;

```

5) To successfully use the external function to detokenize 

```
select detokenize('d2037178-646f-42c9-b73e-c3edf10d9805');

select detokenize(column_name), column_name from table_name;

```