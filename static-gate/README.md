# Static Gate - Go AST Static Analysis Tool

[![Go Version](https://img.shields.io/badge/Go-%3E%3D%201.18-blue)](https://golang.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Static Gate is a powerful, extensible Go AST static analysis tool designed for static code analysis and security detection. Built with Go's standard AST parsing libraries, it provides comprehensive code quality checks, security analysis, and CI/CD integration.

## 🚀 Features

### Core Capabilities
- **AST-based Analysis**: Uses Go's `go/ast`, `go/parser`, and `go/token` packages for accurate parsing
- **Plugin Architecture**: Extensible rules engine with easy rule registration
- **Multiple Output Formats**: JSON, XML, HTML, and Plain Text reports
- **Concurrent Processing**: High-performance parallel file analysis
- **Configuration Management**: YAML-based configuration with multiple levels
- **CI/CD Integration**: Exit codes and optimized configurations for automation

### Built-in Rules

#### Security Rules
- **Dangerous Exec Commands**: Detects `exec.Command` calls that may be exploitable
- **Dangerous OS Operations**: Identifies risky file system operations (`os.Remove`, `os.RemoveAll`, etc.)
- **Hardcoded Secrets**: Finds potential passwords, API keys, and tokens in code

#### Code Quality Rules
- **Naming Conventions**: Enforces Go naming conventions (camelCase/PascalCase)
- **Import Restrictions**: Prevents usage of dangerous or discouraged packages
- **Cyclomatic Complexity**: Identifies overly complex functions

## 📦 Installation

### Binary Installation
```bash
# Download and install the latest release
go install github.com/your-org/static-gate/cmd/static-gate@latest
```

### From Source
```bash
git clone https://github.com/your-org/static-gate.git
cd static-gate
go build -o static-gate cmd/static-gate/main.go
```

## 🛠️ Quick Start

### Basic Usage
```bash
# Analyze current directory
static-gate

# Analyze specific directory
static-gate ./src

# List all available rules
static-gate -list-rules

# Generate HTML report
static-gate -format=html -output=report.html ./src
```

### Configuration
Create a `.static-gate.yaml` file in your project root:

```yaml
rules:
  - id: security.dangerous-exec
    enabled: true
    severity: error
  - id: naming.camelcase
    enabled: true
    severity: warning

ignore_dirs:
  - vendor
  - .git

output_format: json
concurrent: true
exit_on_findings: true
```

## 📖 Usage Guide

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-path` | Path to analyze | `.` |
| `-config` | Configuration file path | Auto-detected |
| `-format` | Output format (json/xml/html/text) | `json` |
| `-output` | Output file path | stdout |
| `-list-rules` | List all available rules | `false` |
| `-verbose` | Verbose output | `false` |
| `-version` | Show version | `false` |

### Configuration File

The configuration file supports the following structure:

```yaml
# Rules configuration
rules:
  - id: security.dangerous-exec
    enabled: true
    severity: error
    params:
      max_args: "5"

# Ignore patterns
ignore_files:
  - "*.pb.go"
  - "*_test.go"

ignore_dirs:
  - "vendor"
  - ".git"

# Output settings
output_format: json
output_file: ""

# Performance settings
concurrent: true
max_goroutines: 4

# CI/CD settings
exit_on_findings: true
```

### Rule Configuration

Each rule can be configured with:
- `id`: Unique rule identifier
- `enabled`: Enable/disable the rule
- `severity`: Override rule severity (error/warning/info)
- `params`: Rule-specific parameters

## 🔧 Advanced Usage

### Custom Rules

Create custom rules by implementing the `pkg.Rule` interface:

```go
package myrules

import (
    "go/ast"
    "go/token"
    "static-gate/pkg"
)

type MyCustomRule struct {
    // Rule implementation
}

func (r *MyCustomRule) ID() string { return "custom.my-rule" }
func (r *MyCustomRule) Name() string { return "My Custom Rule" }
func (r *MyCustomRule) Description() string { return "Description of my rule" }
func (r *MyCustomRule) Severity() pkg.Severity { return pkg.SeverityWarning }
func (r *MyCustomRule) Category() string { return "custom" }

func (r *MyCustomRule) Check(file *ast.File, fset *token.FileSet, filename string) []pkg.Finding {
    // Implementation here
    return []pkg.Finding{}
}
```

### CI/CD Integration

#### GitHub Actions
```yaml
name: Static Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-go@v3
      with:
        go-version: 1.19
    - name: Install Static Gate
      run: go install github.com/your-org/static-gate/cmd/static-gate@latest
    - name: Run Analysis
      run: static-gate -config=configs/ci.yaml -format=json -output=analysis.json
    - name: Upload Results
      uses: actions/upload-artifact@v3
      with:
        name: static-analysis
        path: analysis.json
```

#### Jenkins Pipeline
```groovy
pipeline {
    agent any
    
    stages {
        stage('Static Analysis') {
            steps {
                sh 'static-gate -config=configs/ci.yaml -format=html -output=report.html'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'report.html',
                    reportName: 'Static Analysis Report'
                ])
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'report.html', fingerprint: true
        }
    }
}
```

### Output Formats

#### JSON Output
```json
{
  "timestamp": "2023-12-07T10:30:00Z",
  "findings": [
    {
      "rule_id": "security.dangerous-exec",
      "message": "Dangerous exec.Command call detected",
      "severity": "error",
      "file": "example.go",
      "line": 15,
      "column": 8,
      "category": "security",
      "description": "exec.Command calls can be dangerous if user input is not properly sanitized"
    }
  ],
  "summary": {
    "error_count": 1,
    "warning_count": 2,
    "info_count": 1,
    "total_count": 4
  }
}
```

#### HTML Output
The HTML format generates a comprehensive web-based report with:
- Color-coded severity levels
- File-based organization
- Detailed descriptions
- Summary statistics

## 🏗️ Architecture

### Project Structure
```
static-gate/
├── cmd/                    # Command line interface
│   └── static-gate/
│       └── main.go
├── internal/               # Internal packages
│   ├── analyzer/          # Core AST analysis engine
│   ├── rules/             # Built-in rules implementation
│   ├── config/            # Configuration management
│   ├── reporter/          # Output format handlers
│   └── utils/             # Utility functions
├── pkg/                   # Public API and interfaces
│   └── types.go           # Core types and interfaces
├── configs/               # Configuration examples
├── examples/              # Example code for testing
└── docs/                  # Documentation
```

### Core Components

1. **Analyzer**: Manages AST parsing and rule execution
2. **Rules Engine**: Plugin-based rule system with registry
3. **Configuration**: YAML-based configuration with defaults
4. **Reporter**: Multi-format output generation
5. **CLI**: Command-line interface with comprehensive options

## 🧪 Testing

Run the tool on the provided examples:

```bash
# Test with bad code (should find issues)
static-gate ./examples/bad_code.go

# Test with good code (should find fewer/no issues)
static-gate ./examples/good_code.go

# Generate HTML report for visual inspection
static-gate -format=html -output=test-report.html ./examples/
```

## 🚦 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, no issues found or `exit_on_findings` disabled |
| 1 | Error-level findings detected (when `exit_on_findings` enabled) |
| 2 | Tool execution error (configuration, parsing, etc.) |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

### Adding New Rules

1. Create rule struct implementing `pkg.Rule` interface
2. Add rule to registry in `internal/rules/registry.go`
3. Add configuration to default config files
4. Create tests and documentation
5. Add example code demonstrating the rule

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub Issues
- **Documentation**: Check the [docs/](docs/) directory
- **Examples**: See [examples/](examples/) for usage examples

## 🎯 Roadmap

- [ ] More built-in security rules
- [ ] Integration with popular Go tools (golint, gofmt, etc.)
- [ ] Support for custom rule plugins
- [ ] IDE integrations (VS Code, GoLand)
- [ ] Web-based configuration generator
- [ ] Performance optimizations for large codebases
- [ ] Integration with security scanning platforms