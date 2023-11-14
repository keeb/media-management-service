package main

import (
	"fmt"
	"net/http"
	"io/ioutil"
	"os"

	"encoding/json"

	"github.com/mmcdole/gofeed"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

type Feed struct {
	Updated string `json:"updated,"`
	Shows   []Show `json:"show,omitempty"`
}

type Show struct {
	Title    string `json:"name,omitempty"`
	Magnet   string `json:"magnet,omitempty"`
	Seeds    string `json:"seeds,omitempty"`
	Peers    string `json:"peers,omitempty"`
	Verified string `json:"verified,omitempty"`
	Pubdate  string `json:"pubdate,omitempty"`
	FileName string `json:"filename,omitempty"`
}

func fromItem(item *gofeed.Item) Show {
	s := Show{}

	s.Title = item.Title
	s.Pubdate = item.Published

	for _, ext := range item.Extensions {
		s.FileName = ext["fileName"][0].Value
		s.Magnet = ext["magnetURI"][0].Value
		s.Seeds = ext["seeds"][0].Value
		s.Peers = ext["peers"][0].Value
		s.Verified = ext["verified"][0].Value

	}
	return s
}

func parseFeed(feed *gofeed.Feed) Feed {
	f := Feed{}
	f.Updated = feed.Updated
	s := make([]Show, 0)
	for _, link := range feed.Items {
		show := fromItem(link)
		s = append(s, show)
	}
	f.Shows = s
	return f
}

func feedToJSON(feed Feed) string {
	b, err := json.Marshal(feed)
	check(err)
	return string(b)
}

func main() {
	// TODO: write --help flag
	// TODO: write --output flag
	// TODO: add error handling in the case of the feed not being available
	
	fp := gofeed.NewParser()
	rss, e := http.Get("https://eztv.ag/ezrss.xml") // TODO: make this a flag
	check(e)
	feed, e := fp.Parse(rss.Body)
	check(e)


	parsedFeed := parseFeed(feed)


	// create a file if it doesn't exist called updated
	// if the file exists, check if the updated field is the same as the feed
	// if it is, exit
	// if it isn't, write the new updated field to the file and print the json
	// this is to stop from processing the same feed multiple times.
	
	updated := "updated"
	data, err := ioutil.ReadFile(updated)
	check(err)
	if string(data) == parsedFeed.Updated {
		os.Exit(1)
	}

	ioutil.WriteFile(updated, []byte(parsedFeed.Updated), 0644)

	fmt.Println(feedToJSON(parsedFeed))
	os.Exit(0)
}
