package analyzer

import (
	"fmt"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"

	"static-gate/internal/config"
	"static-gate/pkg"
)

// Analyzer provides static analysis capabilities
type Analyzer struct {
	config   *pkg.Config
	rules    map[string]pkg.Rule
	fileSet  *token.FileSet
	findings []pkg.Finding
	mu       sync.Mutex
}

// New creates a new analyzer instance
func New(cfg *pkg.Config, rules []pkg.Rule) *Analyzer {
	ruleMap := make(map[string]pkg.Rule)
	for _, rule := range rules {
		ruleMap[rule.ID()] = rule
	}

	return &Analyzer{
		config:  cfg,
		rules:   ruleMap,
		fileSet: token.NewFileSet(),
	}
}

// AnalyzeProject analyzes an entire project
func (a *Analyzer) AnalyzeProject(projectPath string) (*pkg.AnalysisResult, error) {
	start := time.Now()
	
	files, err := a.findGoFiles(projectPath)
	if err != nil {
		return nil, fmt.Errorf("failed to find Go files: %w", err)
	}

	if a.config.Concurrent {
		err = a.analyzeFilesConcurrently(files)
	} else {
		err = a.analyzeFilesSequentially(files)
	}

	if err != nil {
		return nil, err
	}

	duration := time.Since(start)
	
	return &pkg.AnalysisResult{
		Findings:     a.findings,
		FilesScanned: len(files),
		RulesApplied: len(a.getEnabledRules()),
		Duration:     duration.String(),
		Summary:      a.generateSummary(),
	}, nil
}

// AnalyzeFile analyzes a single Go file
func (a *Analyzer) AnalyzeFile(filename string) ([]pkg.Finding, error) {
	if config.IsIgnored(filename, a.config) {
		return nil, nil
	}

	src, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to read file %s: %w", filename, err)
	}

	file, err := parser.ParseFile(a.fileSet, filename, src, parser.ParseComments)
	if err != nil {
		return nil, fmt.Errorf("failed to parse file %s: %w", filename, err)
	}

	var findings []pkg.Finding
	enabledRules := a.getEnabledRules()
	
	for _, rule := range enabledRules {
		ruleFindings := rule.Check(file, a.fileSet, filename)
		findings = append(findings, ruleFindings...)
	}

	return findings, nil
}

// findGoFiles recursively finds all Go files in a project
func (a *Analyzer) findGoFiles(root string) ([]string, error) {
	var files []string

	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			if config.IsIgnored(path, a.config) {
				return filepath.SkipDir
			}
			return nil
		}

		if strings.HasSuffix(path, ".go") && !config.IsIgnored(path, a.config) {
			files = append(files, path)
		}

		return nil
	})

	return files, err
}

// analyzeFilesSequentially analyzes files one by one
func (a *Analyzer) analyzeFilesSequentially(files []string) error {
	for _, file := range files {
		findings, err := a.AnalyzeFile(file)
		if err != nil {
			return err
		}
		a.findings = append(a.findings, findings...)
	}
	return nil
}

// analyzeFilesConcurrently analyzes files concurrently
func (a *Analyzer) analyzeFilesConcurrently(files []string) error {
	maxGoroutines := a.config.MaxGoroutines
	if maxGoroutines <= 0 {
		maxGoroutines = runtime.NumCPU()
	}

	semaphore := make(chan struct{}, maxGoroutines)
	var wg sync.WaitGroup
	var analysisError error

	for _, file := range files {
		wg.Add(1)
		go func(filename string) {
			defer wg.Done()
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			findings, err := a.AnalyzeFile(filename)
			if err != nil {
				a.mu.Lock()
				if analysisError == nil {
					analysisError = err
				}
				a.mu.Unlock()
				return
			}

			a.mu.Lock()
			a.findings = append(a.findings, findings...)
			a.mu.Unlock()
		}(file)
	}

	wg.Wait()
	return analysisError
}

// getEnabledRules returns only the enabled rules
func (a *Analyzer) getEnabledRules() []pkg.Rule {
	var enabled []pkg.Rule
	
	for _, ruleConfig := range a.config.Rules {
		if ruleConfig.Enabled {
			if rule, exists := a.rules[ruleConfig.ID]; exists {
				enabled = append(enabled, rule)
			}
		}
	}
	
	return enabled
}

// generateSummary creates a summary of findings
func (a *Analyzer) generateSummary() pkg.Summary {
	summary := pkg.Summary{}
	
	for _, finding := range a.findings {
		summary.TotalCount++
		switch finding.Severity {
		case pkg.SeverityError:
			summary.ErrorCount++
		case pkg.SeverityWarning:
			summary.WarningCount++
		case pkg.SeverityInfo:
			summary.InfoCount++
		}
	}
	
	return summary
}

// HasErrors returns true if there are any error-level findings
func (a *Analyzer) HasErrors() bool {
	for _, finding := range a.findings {
		if finding.Severity == pkg.SeverityError {
			return true
		}
	}
	return false
}