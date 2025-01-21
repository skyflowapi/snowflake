/*
Copyright (c) 2023 Skyflow, Inc.
*/
package detokenize_test

import (
	"encoding/json"
	"fmt"

	. "github.com/onsi/ginkgo/v2"
	"gotest.tools/assert"

	SD "github.com/skyflowapi/snowflake/lambda/detokenize"
)

var _ = Describe("Testing Get Token Array", func() {
	It("TestGetTokenArray", func() {
		sampleTokenJSON := `{ "data": [  [ 0, "3d1dfb71-0550-4ed4-ad8f-95a9020de54c", "4166b044-2dd2-47e2-9ef8-0f415c63a582" ] , [ 1, "ea4f59db-f3fe-44ca-8c27-a01e488f53ad", "743db625-abdb-4e28-b96c-714aa9f3b060" ] ] }`

		var sampleTokenReq SD.TokenRequest
		err := json.Unmarshal([]byte(sampleTokenJSON), &sampleTokenReq)
		if err != nil {
			fmt.Println(err)
		}
		value, _ := SD.GetTokenArray(sampleTokenReq)
		finalTokens := []string{"3d1dfb71-0550-4ed4-ad8f-95a9020de54c", "4166b044-2dd2-47e2-9ef8-0f415c63a582", "ea4f59db-f3fe-44ca-8c27-a01e488f53ad", "743db625-abdb-4e28-b96c-714aa9f3b060"}

		for counter := 0; counter < len(finalTokens); counter++ {
			assert.Equal(GinkgoT(), value[counter], finalTokens[counter])
		}
	})
})
