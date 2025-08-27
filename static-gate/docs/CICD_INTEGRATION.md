# CI/CD Integration Guide for Static Gate

This guide shows how to integrate Static Gate into your CI/CD pipelines.

## GitHub Actions

Create `.github/workflows/static-analysis.yml`:

```yaml
name: Static Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Go
      uses: actions/setup-go@v3
      with:
        go-version: 1.19
    
    - name: Install Static Gate
      run: |
        cd static-gate
        go build -o static-gate cmd/static-gate/main.go
        sudo mv static-gate /usr/local/bin/
    
    - name: Run Static Analysis
      run: static-gate -config=static-gate/configs/ci.yaml -format=json -output=static-analysis.json .
    
    - name: Upload Analysis Results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: static-analysis-report
        path: static-analysis.json
    
    - name: Generate HTML Report
      if: always()
      run: static-gate -config=static-gate/configs/ci.yaml -format=html -output=static-analysis.html .
    
    - name: Upload HTML Report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: static-analysis-html
        path: static-analysis.html
```

## Jenkins Pipeline

Create a `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    tools {
        go 'go-1.19'
    }
    
    environment {
        STATIC_GATE_PATH = './static-gate'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Static Gate') {
            steps {
                dir('static-gate') {
                    sh 'go build -o static-gate cmd/static-gate/main.go'
                }
            }
        }
        
        stage('Static Analysis') {
            steps {
                sh '''
                    cd static-gate
                    ./static-gate -config=configs/ci.yaml -format=json -output=../analysis.json ..
                    ./static-gate -config=configs/ci.yaml -format=html -output=../analysis.html ..
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'analysis.json,analysis.html', fingerprint: true
                    
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'analysis.html',
                        reportName: 'Static Analysis Report'
                    ])
                }
            }
        }
    }
    
    post {
        failure {
            emailext (
                subject: "Static Analysis Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Static analysis found critical issues. Check the report at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

## GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - analyze

variables:
  GO_VERSION: "1.19"

build-static-gate:
  stage: build
  image: golang:$GO_VERSION
  script:
    - cd static-gate
    - go mod tidy
    - go build -o static-gate cmd/static-gate/main.go
  artifacts:
    paths:
      - static-gate/static-gate
    expire_in: 1 hour

static-analysis:
  stage: analyze
  image: golang:$GO_VERSION
  dependencies:
    - build-static-gate
  script:
    - cd static-gate
    - ./static-gate -config=configs/ci.yaml -format=json -output=../analysis.json ..
    - ./static-gate -config=configs/ci.yaml -format=html -output=../analysis.html ..
  artifacts:
    reports:
      junit: analysis.json
    paths:
      - analysis.html
      - analysis.json
    expire_in: 1 week
  allow_failure: false
```

## Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  goVersion: '1.19'

steps:
- task: GoTool@0
  inputs:
    version: '$(goVersion)'
  displayName: 'Set up Go'

- script: |
    cd static-gate
    go mod tidy
    go build -o static-gate cmd/static-gate/main.go
  displayName: 'Build Static Gate'

- script: |
    cd static-gate
    ./static-gate -config=configs/ci.yaml -format=json -output=../analysis.json ..
  displayName: 'Run Static Analysis'

- script: |
    cd static-gate
    ./static-gate -config=configs/ci.yaml -format=html -output=../analysis.html ..
  condition: always()
  displayName: 'Generate HTML Report'

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: 'analysis.json'
    failTaskOnFailedTests: true
  condition: always()
  displayName: 'Publish Analysis Results'

- task: PublishHtmlReport@1
  inputs:
    reportDir: '.'
    tabName: 'Static Analysis'
  condition: always()
  displayName: 'Publish HTML Report'
```

## Docker Integration

Create a Dockerfile for the static gate tool:

```dockerfile
FROM golang:1.19-alpine AS builder

WORKDIR /app
COPY static-gate/ .
RUN go mod tidy
RUN go build -o static-gate cmd/static-gate/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/static-gate .
COPY --from=builder /app/configs ./configs

CMD ["./static-gate"]
```

Build and use:

```bash
docker build -t static-gate:latest .
docker run --rm -v $(pwd):/workspace static-gate:latest -path=/workspace
```

## Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: static-gate
        name: Static Gate Analysis
        entry: ./static-gate/static-gate
        language: system
        files: '\.go$'
        pass_filenames: false
        args: ['-config=static-gate/configs/default.yaml', '.']
```

## Make Integration

Add to your `Makefile`:

```makefile
.PHONY: static-analysis
static-analysis:
	cd static-gate && go build -o static-gate cmd/static-gate/main.go
	./static-gate/static-gate -config=static-gate/configs/default.yaml .

.PHONY: static-analysis-ci
static-analysis-ci:
	cd static-gate && go build -o static-gate cmd/static-gate/main.go
	./static-gate/static-gate -config=static-gate/configs/ci.yaml -format=json -output=analysis.json .

.PHONY: static-analysis-report
static-analysis-report:
	cd static-gate && go build -o static-gate cmd/static-gate/main.go
	./static-gate/static-gate -config=static-gate/configs/default.yaml -format=html -output=static-analysis-report.html .
	@echo "Report generated: static-analysis-report.html"
```

## Configuration Examples

### Strict Security Configuration
```yaml
# strict-security.yaml
rules:
  - id: security.dangerous-exec
    enabled: true
    severity: error
  - id: security.dangerous-os
    enabled: true
    severity: error
  - id: security.hardcoded-secrets
    enabled: true
    severity: error
  - id: imports.restricted
    enabled: true
    severity: error
  - id: naming.camelcase
    enabled: false
  - id: quality.complexity
    enabled: false

exit_on_findings: true
output_format: json
```

### Development Configuration
```yaml
# development.yaml
rules:
  - id: security.dangerous-exec
    enabled: true
    severity: warning
  - id: security.dangerous-os
    enabled: true
    severity: warning
  - id: security.hardcoded-secrets
    enabled: true
    severity: info
  - id: naming.camelcase
    enabled: true
    severity: info
  - id: imports.restricted
    enabled: true
    severity: info
  - id: quality.complexity
    enabled: true
    severity: info

ignore_files:
  - "*_test.go"
  - "mock_*.go"

exit_on_findings: false
output_format: text
```

## Best Practices

1. **Start Gradually**: Begin with security rules only, then add quality rules
2. **Use Different Configs**: Stricter rules for CI/CD, relaxed for development
3. **Ignore Generated Code**: Always ignore auto-generated files
4. **Regular Updates**: Keep the tool and rules updated
5. **Team Alignment**: Ensure team agrees on rule configurations
6. **Documentation**: Document any rule customizations

## Troubleshooting

### Common Issues

1. **Build Failures**: Ensure Go version compatibility
2. **False Positives**: Adjust rule sensitivity or add ignore patterns
3. **Performance**: Use concurrent processing for large codebases
4. **Integration**: Test CI/CD integration in staging first

### Performance Tuning

```yaml
# For large codebases
concurrent: true
max_goroutines: 8

ignore_dirs:
  - vendor
  - .git
  - node_modules
  - dist
  - build
```