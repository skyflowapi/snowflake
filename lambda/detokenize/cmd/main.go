package main

import (
	"github.com/aws/aws-lambda-go/lambda"

	m "snowflake/lambda/detokenize"
)

func main() {
	lambda.Start(m.HandleDetokenizeRequest)
}