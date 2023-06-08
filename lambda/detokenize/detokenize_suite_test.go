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
