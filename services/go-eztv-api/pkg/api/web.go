package api

import (
	"fmt"
	"io"
	"net/http"
)

func MakeRequestQuery(request Request) string {
	
	if request.ImdbId != 0 {
		s := fmt.Sprintf("?imdb_id=%d", request.ImdbId)
		return s
	}

	queryString := "?"
	if request.Page != 0 {
		queryString += fmt.Sprintf("&page=%d", request.Page)
	}
	if request.Limit != 0 {
		queryString += fmt.Sprintf("&limit=%d", request.Limit)
	}

	return queryString 
}


func GetTopTorrents(amount int) Result {
	return FetchResult(Request{Limit: amount})
}

func FetchResult (request Request) Result {
	query := MakeRequestQuery(request)
	content, e := http.Get("https://eztv.re/api/get-torrents" + query)
	Check(e)

	defer content.Body.Close()

	if content.StatusCode != http.StatusOK {
        _ = fmt.Errorf("status error: %v", content.StatusCode)
		return Result{}
    }

	json, _ := io.ReadAll(content.Body)

	return ParseJson(json)
}

func GetTorrents() Result {
	return FetchResult(Request{})
}