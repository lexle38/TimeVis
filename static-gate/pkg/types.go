package pkg

import (
	"go/ast"
	"go/token"
)

// Severity represents the severity level of a finding
type Severity string

const (
	SeverityError   Severity = "error"
	SeverityWarning Severity = "warning"
	SeverityInfo    Severity = "info"
)

// Finding represents a static analysis finding
type Finding struct {
	RuleID      string            `json:"rule_id"`
	Message     string            `json:"message"`
	Severity    Severity          `json:"severity"`
	File        string            `json:"file"`
	Line        int               `json:"line"`
	Column      int               `json:"column"`
	Category    string            `json:"category"`
	Description string            `json:"description,omitempty"`
	Metadata    map[string]string `json:"metadata,omitempty"`
}

// Rule represents a static analysis rule
type Rule interface {
	ID() string
	Name() string
	Description() string
	Severity() Severity
	Category() string
	Check(file *ast.File, fset *token.FileSet, filename string) []Finding
}

// Config represents the configuration for static analysis
type Config struct {
	Rules          []RuleConfig `yaml:"rules"`
	IgnoreFiles    []string     `yaml:"ignore_files"`
	IgnoreDirs     []string     `yaml:"ignore_dirs"`
	OutputFormat   string       `yaml:"output_format"`
	OutputFile     string       `yaml:"output_file"`
	Concurrent     bool         `yaml:"concurrent"`
	MaxGoroutines  int          `yaml:"max_goroutines"`
	ExitOnFindings bool         `yaml:"exit_on_findings"`
}

// RuleConfig represents configuration for a specific rule
type RuleConfig struct {
	ID       string            `yaml:"id"`
	Enabled  bool              `yaml:"enabled"`
	Severity Severity          `yaml:"severity,omitempty"`
	Params   map[string]string `yaml:"params,omitempty"`
}

// Reporter interface for different output formats
type Reporter interface {
	Report(findings []Finding) ([]byte, error)
	Format() string
}

// AnalysisResult contains the results of static analysis
type AnalysisResult struct {
	Findings     []Finding `json:"findings"`
	FilesScanned int       `json:"files_scanned"`
	RulesApplied int       `json:"rules_applied"`
	Duration     string    `json:"duration"`
	Summary      Summary   `json:"summary"`
}

// Summary provides a summary of analysis results
type Summary struct {
	ErrorCount   int `json:"error_count"`
	WarningCount int `json:"warning_count"`
	InfoCount    int `json:"info_count"`
	TotalCount   int `json:"total_count"`
}