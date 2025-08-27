package example

import (
	"fmt"
	"log"
	"os"
)

// GoodExample demonstrates clean, secure Go code
type GoodExample struct {
	Name    string
	Version string
}

// NewGoodExample creates a new instance with proper naming
func NewGoodExample(name, version string) *GoodExample {
	return &GoodExample{
		Name:    name,
		Version: version,
	}
}

// ProcessData demonstrates safe data processing
func (g *GoodExample) ProcessData(input []string) []string {
	var result []string
	
	for _, item := range input {
		if item != "" {
			processed := fmt.Sprintf("%s: %s", g.Name, item)
			result = append(result, processed)
		}
	}
	
	return result
}

// SafeFileOperation demonstrates safe file operations with proper error handling
func SafeFileOperation(filename string) error {
	// Get API key from environment variable instead of hardcoding
	apiKey := os.Getenv("API_KEY")
	if apiKey == "" {
		return fmt.Errorf("API_KEY environment variable not set")
	}
	
	// Safe file operation with proper error handling
	file, err := os.Open(filename)
	if err != nil {
		log.Printf("Warning: Could not open file %s: %v", filename, err)
		return err
	}
	defer file.Close()
	
	// Process file safely
	info, err := file.Stat()
	if err != nil {
		return fmt.Errorf("could not get file info: %w", err)
	}
	
	fmt.Printf("File size: %d bytes\n", info.Size())
	return nil
}

// simpleFunction demonstrates low complexity
func simpleFunction(a, b int) int {
	if a > b {
		return a
	}
	return b
}