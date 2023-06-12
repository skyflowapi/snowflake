# Detokenization Lambda for Snowflake

This Detokenization Lambda permits queries such as `select detokenize(‘12ab7c59-18b2-4db8-8b9f-1135a42ba96a’);` to be run directly from the Snowflake session 

To set up the full workflow please see [this](https://docs.google.com/document/d/10qHaY0RfPB3ZVq77_69VkYhj2nzHZ6OvUOwFx-TZ5ag/edit?usp=sharing)

The _snowflake commands_ folder contains commands that must be run in the Snowflake console. 

The _lambda_ folder contains the code to the detokenize lambda that must be uploaded to your AWS Lambda console. 

