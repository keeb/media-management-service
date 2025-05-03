package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"syscall"
)

type Payload struct {
	Magnet string `json:"magnet"`
}

func main() {
	payload := Payload{
		Magnet: os.Args[1],
	}

	json, _ := json.Marshal(payload)


	url := "http://hancock:9200/magnet"

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(json))
	if err != nil {
		fmt.Println("some shit went wrong", err)
		return
	}

	defer resp.Body.Close()
}

func init() {
	kernel32 := syscall.NewLazyDLL("kernel32.dll")
	proc := kernel32.NewProc("GetConsoleWindow")
	handle, _, _ := proc.Call()

	if handle != 0 {
		user32 := syscall.NewLazyDLL("user32.dll")
		proc := user32.NewProc("ShowWindow")
		_, _, _ = proc.Call(handle, uintptr(0))
	}
}

