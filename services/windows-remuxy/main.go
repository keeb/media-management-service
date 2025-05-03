package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"strings"
)

func test() {

}

func main() {
	dirPath := "Y:/streams"

	directoryContents, err := ioutil.ReadDir(dirPath)

	if err != nil {
		log.Fatalf("Failed to read directory: %v", err)
	}

	fmt.P

}
