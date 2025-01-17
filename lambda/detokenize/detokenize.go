/*
Copyright (c) 2023 Skyflow, Inc.
*/

package detokenize

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"

	"github.com/aws/aws-lambda-go/events"
	saUtil "github.com/skyflowapi/skyflow-go/serviceaccount/util"
	"google.golang.org/protobuf/encoding/protojson"

	proto "github.com/skyflowapi/snowflake/lambda/detokenize/proto"
)

var bearerToken = ""

const (
	// AWSSecretsExtensionBaseEndpoint is the Base Endpoint for AWS Secrets Extension
	AWSSecretsExtensionBaseEndpoint = "http://localhost:2773/secretsmanager/get?secretId=%s"
	// AWSSecretsExtensionTokenHeaderName is the Token Header for AWS Secrets Extension
	AWSSecretsExtensionTokenHeaderName = "X-Aws-Parameters-Secrets-Token"
	// maxNumberOfColumns is the maximum number of columns permitted in a detokenization request
	maxNumberOfColumns = 10
	// maxNumberOfTokens is the maximum number of tokens that can be detokenized
	maxNumberOfTokens = 100
)

// TokenRequest unmarshals request body
type TokenRequest struct {
	Data [][]interface{} `json:"data"`
}

// GetToken is called by the HandleDetokenizeRequest  to fetch Bearer Token.
func GetToken() (string, error) {
	secretValue, err := getSecretValueViaLambdaExtension(AWSSecretsExtensionBaseEndpoint)
	if err != nil {
		log.Printf("error getting credentials from lambda secret extension, err: %v\n", err)
		return "", err
	}
	if saUtil.IsExpired(bearerToken) {
		newToken, err2 := saUtil.GenerateBearerTokenFromCreds(secretValue)
		if err2 != nil {
			log.Printf("error generating bearer token, err: %v\n", err2)
			return "", err2
		}
		bearerToken = newToken.AccessToken
		return bearerToken, nil
	}
	return bearerToken, nil
}

// GetTokenArray is called by the HandleDetokenizeRequest to create an array of tokens
func GetTokenArray(tokenReq TokenRequest) ([]string, error) {
	finalTokens := []string{}
	numberOfColumns := len(tokenReq.Data[0])
	numberOfRows := len(tokenReq.Data)

	if numberOfColumns > maxNumberOfColumns {
		err := fmt.Errorf("number of columns cannot be greater than 10")
		log.Println(err.Error())
		return nil, err
	}

	for rowIndex := 0; rowIndex < numberOfRows; rowIndex++ {
		for columnIndex := 1; columnIndex < numberOfColumns; columnIndex++ {
			tokenVal := tokenReq.Data[rowIndex][columnIndex].(string)
			finalTokens = append(finalTokens, tokenVal)
		}
	}
	return finalTokens, nil
}

// detokenize takes in a Vault URL, Bearer Token, list of tokens and Enable Response Translator and issues a detokenize call to Skyflow's backend.
func detokenize(vaultURL, bearerToken string, tokens []string, enableResponseTranslator string) (*proto.DetokenizeResponse, string, error) {
	if vaultURL == "" {
		err := errors.New("vaultURL must be non-empty string")
		log.Println(err.Error())
		return nil, "", err
	}

	if bearerToken == "" {
		err := errors.New("bearerToken must be non-empty string")
		log.Println(err.Error())
		return nil, "", err
	}

	if len(tokens) < 1 {
		err := errors.New("at least one token must be supplied")
		log.Println(err.Error())
		return nil, "", err
	}

	payload := proto.DetokenizePayload{DetokenizationParameters: []*proto.DetokenizeRecordRequest{}, DownloadURL: true}
	for _, token := range tokens {
		payload.DetokenizationParameters = append(payload.DetokenizationParameters, &proto.DetokenizeRecordRequest{Token: token, Redaction: proto.RedactionEnum_PLAIN_TEXT})
	}

	var buf bytes.Buffer
	if err := json.NewEncoder(&buf).Encode(payload); err != nil {
		err = fmt.Errorf("error encoding detokenize payload, err: %v", err)
		log.Println(err.Error())
		return nil, "", err
	}

	client := http.DefaultClient
	req, err := http.NewRequest(http.MethodPost, fmt.Sprintf("%s/detokenize", vaultURL), &buf)
	if err != nil {
		err = fmt.Errorf("error creating detokenize request: %v", err)
		log.Println(err.Error())
		return nil, "", err
	}

	var res *http.Response
	req.Header = http.Header{"Authorization": {fmt.Sprintf("Bearer %s", bearerToken)}}

	if err = Retry(3, 100, 2, func() error {
		res, err = client.Do(req)
		if err != nil {
			err = fmt.Errorf("error doing detokenize request: %v", err)
			log.Println(err.Error())
			return err
		}
		return nil
	}); err != nil {
		return nil, "", err
	}

	type ErrorResponse struct {
		Error struct {
			Message string `json:"message"`
		} `json:"error"`
	}

	resBodyBytes, _ := io.ReadAll(res.Body)
	var detokenizeResponse proto.DetokenizeResponse
	if err = protojson.Unmarshal(resBodyBytes, &detokenizeResponse); err != nil {
		var response ErrorResponse
		var message string
		if err2 := json.Unmarshal(resBodyBytes, &response); err2 != nil {
			message = "Error parsing missing token values"
			log.Printf("Could not unmarshal detokenize response. Error: %v\n\n", err2)
		} else {
			if enableResponseTranslator == "true" {
				message = string(resBodyBytes)
				log.Println(message)
			} else {
				message = response.Error.Message
				log.Println(message)
			}
		}
		return nil, message, err
	}
	return &detokenizeResponse, "", nil
}

// HandleDetokenizeRequest is a handler to detokenize tokens passed in the body of the request.
func HandleDetokenizeRequest(_ context.Context, event events.APIGatewayProxyRequest) (*events.APIGatewayProxyResponse, error) {
	bearerToken, err := GetToken()
	if err != nil {
		log.Println("error getting bearer token from get token")
		return nil, fmt.Errorf("error getting bearer token from get token")
	}

	vaultID, ok := os.LookupEnv("VAULT_ID")
	if !ok {
		log.Println("VAULT_ID is not defined")
		return nil, fmt.Errorf("VAULT_ID is not defined")
	}

	vaultURI, ok := os.LookupEnv("VAULT_URL")
	if !ok {
		log.Println("VAULT_URL is not defined")
		return nil, fmt.Errorf("VAULT_URL is not defined")
	}
	vaultURL := vaultURI + "/v1/vaults/" + vaultID

	b := []byte(event.Body)

	var tokenReq TokenRequest
	if err := json.Unmarshal(b, &tokenReq); err != nil {
		log.Printf("error unmarshaling body into token request, err: %v", err)
		return nil, fmt.Errorf("error unmarshaling body, err: %v", err)
	}
	numberOfColumns := len(tokenReq.Data[0])
	numberOfRows := len(tokenReq.Data)
	numberOfTokens := numberOfRows * (numberOfColumns - 1)
	if numberOfTokens > maxNumberOfTokens {
		return &events.APIGatewayProxyResponse{
			StatusCode: http.StatusBadRequest,
			Body:       "Number of tokens cannot be greater than 100",
		}, nil
	}
	finalTokens := []string{}
	finalTokens, err = GetTokenArray(tokenReq)
	if err != nil {
		log.Println("error getting token array")
		return nil, fmt.Errorf("error getting token array")
	}

	enableResponseTranslator, ok := os.LookupEnv("ENABLE_RESPONSE_TRANSLATOR")
	if !ok {
		log.Println("ENABLE_RESPONSE_TRANSLATOR is not defined")
		return nil, fmt.Errorf("ENABLE_RESPONSE_TRANSLATOR is not defined")
	}

	detokRes, message, err := detokenize(vaultURL, bearerToken, finalTokens, enableResponseTranslator)
	if err != nil {
		if enableResponseTranslator == "true" {
			return &events.APIGatewayProxyResponse{
				StatusCode: http.StatusOK,
				Body:       message,
			}, nil

		}
		return &events.APIGatewayProxyResponse{
			StatusCode: http.StatusNotFound,
			Body:       message,
		}, nil
	}

	var detokenizeResponse struct {
		Data [][]any `json:"data"`
	}

	numberOfTokensCnt := 0
	numberOfColumnsParsed := 0
	numberOfDetokenRecords := 0

	for rowIndex := 0; rowIndex < numberOfRows; rowIndex++ {
		numberOfTokensCnt = numberOfTokensCnt + numberOfColumnsParsed
		detokRecord := []string{}
		for input := 0; input < 1; input++ {
			for DetokenRecord := numberOfDetokenRecords; DetokenRecord < numberOfColumns-1+numberOfTokensCnt; DetokenRecord++ {
				detokRecord = append(detokRecord, detokRes.Records[DetokenRecord].Value)
				numberOfDetokenRecords++
			}
			detokenizeResponse.Data = append(detokenizeResponse.Data, []any{rowIndex, detokRecord})
			numberOfColumnsParsed = numberOfColumns - 1
		}
	}

	res, err := json.Marshal(detokenizeResponse)
	if err != nil {
		log.Println("error marshaling detokenized response")
		return nil, fmt.Errorf("error marshaling detokenized response")
	}

	response := string(res)
	log.Printf(response)
	return &events.APIGatewayProxyResponse{
		StatusCode: http.StatusOK,
		Body:       response,
	}, nil
}

// getSecretValueViaLambdaExtension returns string value from secret using Secret Lambda Extension
// See: https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html for more.
func getSecretValueViaLambdaExtension(awsSecretsExtensionBaseEndpoint string) (string, error) {
	secretName, ok := os.LookupEnv("SECRET_NAME")
	if !ok {
		return "", fmt.Errorf("env var 'SECRET_NAME' is missing")
	}
	if secretName == "" {
		return "", fmt.Errorf("env var 'SECRET_NAME' value is empty string")
	}
	sessionToken, ok := os.LookupEnv("AWS_SESSION_TOKEN")
	if !ok {
		return "", fmt.Errorf("env var 'AWS_SESSION_TOKEN' is missing")
	}
	client := http.DefaultClient
	req, err := http.NewRequest(http.MethodGet, fmt.Sprintf(awsSecretsExtensionBaseEndpoint, secretName), nil)
	if err != nil {
		return "", fmt.Errorf("error creating new request: %v", err)
	}

	req.Header = http.Header{AWSSecretsExtensionTokenHeaderName: {sessionToken}}
	var res *http.Response

	if err = Retry(3, 100, 2, func() error {
		res, err = client.Do(req)
		if err != nil {
			return err
		}
		return nil
	}); err != nil {
		return "", err
	}

	body, err := io.ReadAll(res.Body)
	if err != nil {
		return "", fmt.Errorf("error reading response body")
	}
	var access map[string]interface{}
	if er := json.Unmarshal(body, &access); er != nil {
		return "", fmt.Errorf("error unmarshaling response body")
	}

	secretStringValue, ok := (access["SecretString"]).(string)
	if !ok {
		return "", fmt.Errorf("SecretString is not in expected data type (string)")
	}

	return secretStringValue, nil
}
