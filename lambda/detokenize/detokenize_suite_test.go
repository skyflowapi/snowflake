/*
Copyright (c) 2022 Skyflow, Inc.
*/
package detokenize_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

func TestDetokenize(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Detokenize Suite")
}
