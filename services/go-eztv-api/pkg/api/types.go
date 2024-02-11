package api

type Torrent struct {
	Id              int    `json:"id"`
	Hash            string `json:"hash"`
	Filename        string `json:"filename"`
	EpiseoseUrl     string `json:"episode_url"`
	TorrentUrl      string `json:"torrent_url"`
	MagnetUrl       string `json:"magnet_url"`
	Title           string `json:"title"`
	ImdbId          string `json:"imdb_id"`
	Season          string `json:"season"`
	Episode         string `json:"episode"`
	SmallScreenshot string `json:"small_screenshot"`
	LargeScreenshot string `json:"large_screenshot"`
	Seeds           int    `json:"seeds"`
	Peers           int    `json:"peers"`
	ReleaseDate     int    `json:"date_released_unix"`
	SizeBytes       string `json:"size_bytes"`
}

type Result struct {
	Count    int       `json:"torrents_count"`
	Limit    int       `json:"limit"`
	Page     int       `json:"page"`
	Torrents []Torrent `json:"torrents"`
}

type Request struct {
	Limit int
	Page  int
	ImdbId int
}