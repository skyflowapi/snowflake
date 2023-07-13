/*
Copyright (c) 2023 Skyflow, Inc.
*/
package main

import (
	"github.com/aws/aws-lambda-go/lambda"

	m "snowflake/lambda/detokenize"
)

func main() {
	lambda.Start(m.HandleDetokenizeRequest)
}
