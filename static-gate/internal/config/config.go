package config

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
	"static-gate/pkg"
)

// DefaultConfig returns a default configuration
func DefaultConfig() *pkg.Config {
	return &pkg.Config{
		Rules: []pkg.RuleConfig{
			{ID: "security.dangerous-exec", Enabled: true, Severity: pkg.SeverityError},
			{ID: "security.dangerous-os", Enabled: true, Severity: pkg.SeverityError},
			{ID: "security.hardcoded-secrets", Enabled: true, Severity: pkg.SeverityWarning},
			{ID: "naming.camelcase", Enabled: true, Severity: pkg.SeverityWarning},
			{ID: "imports.restricted", Enabled: true, Severity: pkg.SeverityWarning},
			{ID: "quality.complexity", Enabled: true, Severity: pkg.SeverityInfo},
		},
		IgnoreFiles:    []string{},
		IgnoreDirs:     []string{"vendor", ".git", "node_modules"},
		OutputFormat:   "json",
		OutputFile:     "",
		Concurrent:     true,
		MaxGoroutines:  4,
		ExitOnFindings: true,
	}
}

// LoadConfig loads configuration from a file
func LoadConfig(configPath string) (*pkg.Config, error) {
	// Start with default config
	config := DefaultConfig()

	// If no config file specified, return default
	if configPath == "" {
		return config, nil
	}

	// Check if config file exists
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		return nil, fmt.Errorf("config file not found: %s", configPath)
	}

	// Read config file
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	// Parse YAML
	if err := yaml.Unmarshal(data, config); err != nil {
		return nil, fmt.Errorf("failed to parse config file: %w", err)
	}

	return config, nil
}

// FindConfigFile searches for a config file in common locations
func FindConfigFile(startDir string) string {
	configNames := []string{
		".static-gate.yaml",
		".static-gate.yml",
		"static-gate.yaml",
		"static-gate.yml",
	}

	dir := startDir
	for {
		for _, name := range configNames {
			configPath := filepath.Join(dir, name)
			if _, err := os.Stat(configPath); err == nil {
				return configPath
			}
		}

		parent := filepath.Dir(dir)
		if parent == dir {
			break // reached root
		}
		dir = parent
	}

	return ""
}

// SaveConfig saves configuration to a file
func SaveConfig(config *pkg.Config, configPath string) error {
	data, err := yaml.Marshal(config)
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(configPath, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// IsIgnored checks if a file or directory should be ignored
func IsIgnored(path string, config *pkg.Config) bool {
	name := filepath.Base(path)
	dir := filepath.Dir(path)

	// Check ignored files
	for _, pattern := range config.IgnoreFiles {
		if matched, _ := filepath.Match(pattern, name); matched {
			return true
		}
	}

	// Check ignored directories
	for _, pattern := range config.IgnoreDirs {
		if matched, _ := filepath.Match(pattern, name); matched {
			return true
		}
		if matched, _ := filepath.Match(pattern, dir); matched {
			return true
		}
	}

	return false
}