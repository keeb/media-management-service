package main // import "github.com/keeb/eztv-rss-to-json"

import (
	"os"
	"testing"

	"github.com/mmcdole/gofeed"
)


func getRSS() *gofeed.Feed {
	f, e := os.Open("test/ezrss.xml")
	check(e)
	defer f.Close()
	fp := gofeed.NewParser()
	feed, e := fp.Parse(f)
	check(e)
	return feed
}

func TestFromItem(t *testing.T) {
	item := getRSS().Items[0]
	got := fromItem(item)
	want := Show{
		Title:    item.Title,
		Pubdate:  item.Published,
		FileName: item.Extensions["torrent"]["fileName"][0].Value,
		Magnet:   item.Extensions["torrent"]["magnetURI"][0].Value,
		Seeds:    item.Extensions["torrent"]["seeds"][0].Value,
		Peers:    item.Extensions["torrent"]["peers"][0].Value,
		Verified: item.Extensions["torrent"]["verified"][0].Value,
	}
	if got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func TestParseFeed(t *testing.T) {
	got := len(getRSS().Items) 
	want := got > 0
	if !want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func TestPubdate(t *testing.T) {
	got := parseFeed(getRSS()).Updated
	want := "Thu, 12 Jan 2023 19:07:01 -0500"
	if want != got {
		t.Errorf("got %v, want %v", got, want)
	}
}


