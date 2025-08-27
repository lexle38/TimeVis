package main

import (
	"flag"
	"fmt"
	"os"
	"strings"

	"static-gate/internal/analyzer"
	"static-gate/internal/config"
	"static-gate/internal/reporter"
	"static-gate/internal/rules"
	"static-gate/pkg"
)

const (
	version = "1.0.0"
	banner  = `
  ____  _        _   _        ____       _       
 / ___|| |_ __ _| |_(_) ___  / ___| __ _| |_ ___ 
 \___ \| __/ _` + "`" + ` | __| |/ __||  __ / _` + "`" + ` | __/ _ \
  ___) | || (_| | |_| | (__ | |_| | (_| | ||  __/
 |____/ \__\__,_|\__|_|\___| \____|\__,_|\__\___|
                                                
 Go AST Static Analysis Gate Tool v%s
`
)

type CLI struct {
	projectPath  string
	configPath   string
	outputFormat string
	outputFile   string
	listRules    bool
	version      bool
	verbose      bool
	help         bool
}

func main() {
	cli := parseFlags()

	if cli.help {
		printUsage()
		return
	}

	if cli.version {
		fmt.Printf("static-gate version %s\n", version)
		return
	}

	if cli.listRules {
		listAllRules()
		return
	}

	// Load configuration
	cfg, err := config.LoadConfig(cli.configPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading config: %v\n", err)
		os.Exit(1)
	}

	// Override config with CLI flags
	if cli.outputFormat != "" {
		cfg.OutputFormat = cli.outputFormat
	}
	if cli.outputFile != "" {
		cfg.OutputFile = cli.outputFile
	}

	// Create rules registry
	registry := rules.NewRegistry()

	// Create analyzer
	allRules := registry.GetAll()
	analyzer := analyzer.New(cfg, allRules)

	// Analyze project
	result, err := analyzer.AnalyzeProject(cli.projectPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Analysis failed: %v\n", err)
		os.Exit(1)
	}

	// Generate report
	rep := reporter.GetReporter(cfg.OutputFormat)
	output, err := rep.Report(result.Findings)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Report generation failed: %v\n", err)
		os.Exit(1)
	}

	// Output results
	if cfg.OutputFile != "" {
		err = os.WriteFile(cfg.OutputFile, output, 0644)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to write output file: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Report written to: %s\n", cfg.OutputFile)
	} else {
		fmt.Print(string(output))
	}

	// Print summary if verbose or no output file
	if cli.verbose || cfg.OutputFile != "" {
		printSummary(result)
	}

	// Exit with appropriate code
	if cfg.ExitOnFindings && (result.Summary.ErrorCount > 0) {
		os.Exit(1)
	}
}

func parseFlags() *CLI {
	cli := &CLI{}

	flag.StringVar(&cli.projectPath, "path", ".", "Path to Go project or file to analyze")
	flag.StringVar(&cli.configPath, "config", "", "Path to configuration file")
	flag.StringVar(&cli.outputFormat, "format", "", "Output format (json, xml, html, text)")
	flag.StringVar(&cli.outputFile, "output", "", "Output file (default: stdout)")
	flag.BoolVar(&cli.listRules, "list-rules", false, "List all available rules")
	flag.BoolVar(&cli.version, "version", false, "Show version information")
	flag.BoolVar(&cli.verbose, "verbose", false, "Verbose output")
	flag.BoolVar(&cli.help, "help", false, "Show help")

	// Also support -h for help
	flag.BoolVar(&cli.help, "h", false, "Show help")

	flag.Parse()

	// If no explicit project path and there are args, use first arg as path
	if cli.projectPath == "." && flag.NArg() > 0 {
		cli.projectPath = flag.Arg(0)
	}

	// Auto-find config if not specified
	if cli.configPath == "" {
		if foundConfig := config.FindConfigFile(cli.projectPath); foundConfig != "" {
			cli.configPath = foundConfig
		}
	}

	return cli
}

func printUsage() {
	fmt.Printf(banner, version)
	fmt.Println("\nUsage:")
	fmt.Println("  static-gate [options] [path]")
	fmt.Println("\nOptions:")
	flag.PrintDefaults()
	fmt.Println("\nExamples:")
	fmt.Println("  static-gate                          # Analyze current directory")
	fmt.Println("  static-gate ./src                    # Analyze src directory")
	fmt.Println("  static-gate -format=html -output=report.html ./src")
	fmt.Println("  static-gate -config=.static-gate.yaml ./src")
	fmt.Println("  static-gate -list-rules              # List all available rules")
	fmt.Println("\nSupported formats: json, xml, html, text")
}

func listAllRules() {
	registry := rules.NewRegistry()
	rulesList := registry.ListRules()

	fmt.Printf(banner, version)
	fmt.Println("\nAvailable Rules:")
	fmt.Println(strings.Repeat("=", 50))

	categories := make(map[string][]rules.RuleInfo)
	for _, rule := range rulesList {
		categories[rule.Category] = append(categories[rule.Category], rule)
	}

	for category, categoryRules := range categories {
		fmt.Printf("\n%s:\n", strings.ToUpper(category))
		for _, rule := range categoryRules {
			fmt.Printf("  %-30s %s [%s]\n", rule.ID, rule.Name, rule.Severity)
			fmt.Printf("    %s\n", rule.Description)
		}
	}

	fmt.Printf("\nTotal: %d rules\n", len(rulesList))
}

func printSummary(result *pkg.AnalysisResult) {
	fmt.Print("\n" + strings.Repeat("=", 50) + "\n")
	fmt.Printf("Analysis Summary:\n")
	fmt.Printf("  Files Scanned: %d\n", result.FilesScanned)
	fmt.Printf("  Rules Applied: %d\n", result.RulesApplied)
	fmt.Printf("  Duration: %s\n", result.Duration)
	fmt.Printf("  Findings:\n")
	fmt.Printf("    Errors: %d\n", result.Summary.ErrorCount)
	fmt.Printf("    Warnings: %d\n", result.Summary.WarningCount)
	fmt.Printf("    Info: %d\n", result.Summary.InfoCount)
	fmt.Printf("    Total: %d\n", result.Summary.TotalCount)
	fmt.Print(strings.Repeat("=", 50) + "\n")
}