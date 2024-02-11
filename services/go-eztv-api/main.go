package main

import (
	"fmt"

	"github.com/keeb/go-eztv-api/pkg/api"
)

func main() {
	fmt.Println(api.GetTorrents())
}
