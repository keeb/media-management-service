package api

import (
	"os"
	"testing"
)

var result Result // holds the parsed json

func getTestFeed() []byte {
	f, e := os.ReadFile("test/result.json")
	Check(e)
	return f
}

func GetTestStruct() Result {
	if (result.Torrents != nil) {
		return result
	}

	feed := getTestFeed()
	result = ParseJson(feed)
	return result
}
func TestParseTorrentsCount(t *testing.T) {
	result := GetTestStruct()
	got := result.Count
	want := got == 671707
	if !want {
		t.Errorf("got %v want 671707", got)
	}
}

func TestParseTorrentsLimit(t *testing.T) {
	result := GetTestStruct()
	got := result.Limit
	want := got == 10
	if !want {
		t.Errorf("got %v want 10", got)
	}
}

func TestParseTorrentsPage(t *testing.T) {
	result := GetTestStruct()
	got := result.Page
	want := got == 1
	if !want {
		t.Errorf("got %v want 1", got)
	}
}

func TestParseTotalTorrents(t *testing.T) {
	result := GetTestStruct()
	got := len(result.Torrents)
	want := got == 10
	if !want {
		t.Errorf("got %v want 10", got)
	}
}

func TestParseTorrentInfo_Id(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].Id
	want := got == 1922138
	if !want {
		t.Errorf("got %v want 1922138", got)
	}
}

func TestParseTorrentInfo_Hash(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].Hash
	want := got == "ee5302e9fc0aaaec5de0944bd3d257b531ae825c"
	if !want {
		t.Errorf("got %v want ee5302e9fc0aaaec5de0944bd3d257b531ae825c", got)
	}
}

func TestParseTorrentInfo_Filename(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].Filename
	want := got == "Children.Ruin.Everything.S02E16.720p.HEVC.x265-MeGusta[eztv.re].mkv"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_EpiseoseUrl(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].EpiseoseUrl
	want := got == "https://eztv.re/ep/1922138/children-ruin-everything-s02e16-720p-hevc-x265-megusta/"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_TorrentUrl(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].TorrentUrl
	want := got == "https://zoink.ch/torrent/Children.Ruin.Everything.S02E16.720p.HEVC.x265-MeGusta[eztv.re].mkv.torrent"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_MagnetUrl(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].MagnetUrl
	want := got == "magnet:?xt=urn:btih:ee5302e9fc0aaaec5de0944bd3d257b531ae825c&dn=Children.Ruin.Everything.S02E16.720p.HEVC.x265-MeGusta%5Beztv%5D&tr=udp://tracker.opentrackr.org:1337/announce&tr=udp://9.rarbg.me:2970/announce&tr=udp://p4p.arenabg.com:1337/announce&tr=udp://tracker.torrent.eu.org:451/announce&tr=udp://tracker.dler.org:6969/announce&tr=udp://open.stealth.si:80/announce&tr=udp://ipv4.tracker.harry.lu:80/announce&tr=https://opentracker.i2p.rocks:443/announce"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_Title(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].Title
	want := got == "Children Ruin Everything S02E16 720p HEVC x265-MeGusta EZTV"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_ImdbId(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].ImdbId
	want := got == "10738442"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_Season(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].Season
	want := got == "2"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_Episode(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].Episode
	want := got == "16"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_Seeds(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].Seeds
	want := got == 0
	if !want {
		t.Errorf("got %v instead", got)
	}
}
func TestParseTorrentInfo_Peers(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].Peers
	want := got == 0
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_ReleaseDate(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].ReleaseDate
	want := got == 1676944234
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestParseTorrentInfo_Size(t *testing.T) {
	result := GetTestStruct()
	got := result.Torrents[0].SizeBytes
	want := got == "202667997"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestQueryWithImdbRequest(t *testing.T) {
	got := MakeRequestQuery(Request{ImdbId: 2})
	want := got == "?imdb_id=2"
	if !want {
		t.Errorf("got %v instead", got)
	}
}

func TestQueryWithPageAndLimitRequest(t *testing.T) {
	got := MakeRequestQuery(Request{Page: 2, Limit: 10})
	want := got == "?&page=2&limit=10"

	if !want {
		t.Errorf("got %v instead", got)
	}	
}

func TestEmptyQuery (t *testing.T) {
	got := MakeRequestQuery(Request{})
	want := got == "?"
	if !want {
		t.Errorf("got %v instead", got)
	}
}