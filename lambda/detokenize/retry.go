/*
Copyright (c) 2023 Skyflow, Inc.
*/

package detokenize

import "time"

// Retry wraps a function that may return an error and retries the func using exponential backoff.
// attempts is the max number of attempts to execute before returning with the last error
// delay is the initial time to delay in milliseconds
// multiplier is scaling factor, set to 1 for constant wait of delay between attempts
func Retry(attempts, delay, multiplier int, callback func() error) (err error) {
	for i := 0; i < attempts; i++ {
		err = callback()
		if err == nil {
			return nil
		}
		time.Sleep(time.Duration(delay) * time.Millisecond)
		delay *= multiplier // exponential back-off
	}
	return err
}
