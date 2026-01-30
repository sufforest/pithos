package timeutils

import (
	"time"
)

// GetCurrentTime returns the current time as a formatted string
func GetCurrentTime() string {
	return time.Now().Format(time.RFC3339)
}
