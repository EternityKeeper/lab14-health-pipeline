package main

import (
	"encoding/json"
	"log"
	"math/rand"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

type HealthRecord struct {
	Timestamp   string  `json:"timestamp"`
	HeartRate   int     `json:"heart_rate"`
	SystolicBP  int     `json:"systolic_bp"`
	DiastolicBP int     `json:"diastolic_bp"`
	Temperature float64 `json:"temperature"`
	SpO2        int     `json:"spo2"`
}

func generateRecord() HealthRecord {
	return HealthRecord{
		Timestamp:   time.Now().UTC().Format(time.RFC3339),
		HeartRate:   60 + rand.Intn(41),
		SystolicBP:  90 + rand.Intn(51),
		DiastolicBP: 60 + rand.Intn(31),
		Temperature: 36.0 + rand.Float64()*1.5,
		SpO2:        95 + rand.Intn(6),
	}
}

func main() {
	log.Println("Starting health data collector...")

	records := make(chan HealthRecord, 100)
	done := make(chan struct{})
	var wg sync.WaitGroup

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	wg.Add(1)
	go func() {
		defer wg.Done()
		ticker := time.NewTicker(2 * time.Second)
		defer ticker.Stop()
		for {
			select {
			case <-ticker.C:
				record := generateRecord()
				records <- record
				log.Printf("Generated: HR=%d BP=%d/%d Temp=%.1f SpO2=%d",
					record.HeartRate, record.SystolicBP, record.DiastolicBP, record.Temperature, record.SpO2)
			case <-done:
				log.Println("Generator stopping...")
				return
			}
		}
	}()

	wg.Add(1)
	go func() {
		defer wg.Done()
		file, err := os.OpenFile("health_data.json", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			log.Fatalf("Failed to open file: %v", err)
		}
		defer file.Close()

		var batch []HealthRecord
		flushTimer := time.NewTicker(5 * time.Second)
		defer flushTimer.Stop()

		flush := func() {
			if len(batch) == 0 {
				return
			}
			encoder := json.NewEncoder(file)
			for _, r := range batch {
				if err := encoder.Encode(r); err != nil {
					log.Printf("Failed to write record: %v", err)
				}
			}
			log.Printf("Batch written: %d records", len(batch))
			batch = batch[:0]
		}

		for {
			select {
			case record := <-records:
				batch = append(batch, record)
				if len(batch) >= 10 {
					flush()
				}
			case <-flushTimer.C:
				flush()
			case <-done:
				log.Println("Writer stopping, flushing remaining records...")
				for remaining := range records {
					batch = append(batch, remaining)
				}
				flush()
				return
			}
		}
	}()

	sig := <-sigChan
	log.Printf("Received signal: %v. Shutting down...", sig)
	close(done)

	wg.Wait()
	log.Println("Shutdown complete.")
}
