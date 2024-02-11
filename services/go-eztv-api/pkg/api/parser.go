package api

import "encoding/json"

func ParseJson(content []byte) Result {
	// convert json to struct
	var result Result
	e := json.Unmarshal([]byte(content), &result)
	Check(e)
	return result
}