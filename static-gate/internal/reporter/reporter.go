package reporter

import (
	"encoding/json"
	"encoding/xml"
	"fmt"
	"html/template"
	"strings"
	"time"

	"static-gate/pkg"
)

// JSONReporter outputs findings in JSON format
type JSONReporter struct{}

func NewJSONReporter() *JSONReporter {
	return &JSONReporter{}
}

func (r *JSONReporter) Report(findings []pkg.Finding) ([]byte, error) {
	result := struct {
		Timestamp string        `json:"timestamp"`
		Findings  []pkg.Finding `json:"findings"`
		Summary   pkg.Summary   `json:"summary"`
	}{
		Timestamp: time.Now().Format(time.RFC3339),
		Findings:  findings,
		Summary:   generateSummary(findings),
	}

	return json.MarshalIndent(result, "", "  ")
}

func (r *JSONReporter) Format() string {
	return "json"
}

// XMLReporter outputs findings in XML format
type XMLReporter struct{}

func NewXMLReporter() *XMLReporter {
	return &XMLReporter{}
}

func (r *XMLReporter) Report(findings []pkg.Finding) ([]byte, error) {
	result := struct {
		XMLName   xml.Name      `xml:"static-analysis-results"`
		Timestamp string        `xml:"timestamp"`
		Findings  []pkg.Finding `xml:"findings>finding"`
		Summary   pkg.Summary   `xml:"summary"`
	}{
		Timestamp: time.Now().Format(time.RFC3339),
		Findings:  findings,
		Summary:   generateSummary(findings),
	}

	return xml.MarshalIndent(result, "", "  ")
}

func (r *XMLReporter) Format() string {
	return "xml"
}

// PlainTextReporter outputs findings in plain text format
type PlainTextReporter struct{}

func NewPlainTextReporter() *PlainTextReporter {
	return &PlainTextReporter{}
}

func (r *PlainTextReporter) Report(findings []pkg.Finding) ([]byte, error) {
	var builder strings.Builder
	
	builder.WriteString("Static Analysis Report\n")
	builder.WriteString("======================\n\n")
	builder.WriteString(fmt.Sprintf("Generated: %s\n\n", time.Now().Format(time.RFC3339)))
	
	if len(findings) == 0 {
		builder.WriteString("No issues found!\n")
		return []byte(builder.String()), nil
	}

	summary := generateSummary(findings)
	builder.WriteString("Summary:\n")
	builder.WriteString(fmt.Sprintf("  Errors: %d\n", summary.ErrorCount))
	builder.WriteString(fmt.Sprintf("  Warnings: %d\n", summary.WarningCount))
	builder.WriteString(fmt.Sprintf("  Info: %d\n", summary.InfoCount))
	builder.WriteString(fmt.Sprintf("  Total: %d\n\n", summary.TotalCount))

	// Group findings by file
	fileFindings := make(map[string][]pkg.Finding)
	for _, finding := range findings {
		fileFindings[finding.File] = append(fileFindings[finding.File], finding)
	}

	for file, fileFindingsList := range fileFindings {
		builder.WriteString(fmt.Sprintf("File: %s\n", file))
		builder.WriteString(strings.Repeat("-", len(file)+6) + "\n")
		
		for _, finding := range fileFindingsList {
			severitySymbol := getSeveritySymbol(finding.Severity)
			builder.WriteString(fmt.Sprintf("  %s %s:%d:%d - %s (%s)\n",
				severitySymbol, file, finding.Line, finding.Column,
				finding.Message, finding.RuleID))
			if finding.Description != "" {
				builder.WriteString(fmt.Sprintf("    %s\n", finding.Description))
			}
		}
		builder.WriteString("\n")
	}

	return []byte(builder.String()), nil
}

func (r *PlainTextReporter) Format() string {
	return "text"
}

// HTMLReporter outputs findings in HTML format
type HTMLReporter struct{}

func NewHTMLReporter() *HTMLReporter {
	return &HTMLReporter{}
}

func (r *HTMLReporter) Report(findings []pkg.Finding) ([]byte, error) {
	tmpl := template.Must(template.New("report").Parse(htmlTemplate))
	
	data := struct {
		Timestamp string
		Findings  []pkg.Finding
		Summary   pkg.Summary
		FileFindings map[string][]pkg.Finding
	}{
		Timestamp: time.Now().Format("2006-01-02 15:04:05"),
		Findings:  findings,
		Summary:   generateSummary(findings),
		FileFindings: groupFindingsByFile(findings),
	}

	var builder strings.Builder
	err := tmpl.Execute(&builder, data)
	if err != nil {
		return nil, fmt.Errorf("failed to execute HTML template: %w", err)
	}

	return []byte(builder.String()), nil
}

func (r *HTMLReporter) Format() string {
	return "html"
}

// Helper functions
func generateSummary(findings []pkg.Finding) pkg.Summary {
	summary := pkg.Summary{}
	
	for _, finding := range findings {
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

func getSeveritySymbol(severity pkg.Severity) string {
	switch severity {
	case pkg.SeverityError:
		return "✗"
	case pkg.SeverityWarning:
		return "⚠"
	case pkg.SeverityInfo:
		return "ℹ"
	default:
		return "?"
	}
}

func groupFindingsByFile(findings []pkg.Finding) map[string][]pkg.Finding {
	fileFindings := make(map[string][]pkg.Finding)
	for _, finding := range findings {
		fileFindings[finding.File] = append(fileFindings[finding.File], finding)
	}
	return fileFindings
}

// GetReporter returns a reporter based on format string
func GetReporter(format string) pkg.Reporter {
	switch strings.ToLower(format) {
	case "json":
		return NewJSONReporter()
	case "xml":
		return NewXMLReporter()
	case "html":
		return NewHTMLReporter()
	case "text", "plain":
		return NewPlainTextReporter()
	default:
		return NewJSONReporter() // Default to JSON
	}
}

const htmlTemplate = `
<!DOCTYPE html>
<html>
<head>
    <title>Static Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
        .summary { background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .file-section { margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }
        .file-header { background-color: #f8f9fa; padding: 10px; font-weight: bold; }
        .finding { padding: 10px; border-bottom: 1px solid #eee; }
        .finding:last-child { border-bottom: none; }
        .severity-error { border-left: 4px solid #dc3545; }
        .severity-warning { border-left: 4px solid #ffc107; }
        .severity-info { border-left: 4px solid #17a2b8; }
        .location { color: #666; font-size: 0.9em; }
        .rule-id { background-color: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; }
        .description { color: #666; font-style: italic; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Static Analysis Report</h1>
        <p>Generated: {{.Timestamp}}</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <p>Errors: {{.Summary.ErrorCount}} | Warnings: {{.Summary.WarningCount}} | Info: {{.Summary.InfoCount}} | Total: {{.Summary.TotalCount}}</p>
    </div>

    {{if eq (len .Findings) 0}}
        <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px;">
            <strong>Great!</strong> No issues found.
        </div>
    {{else}}
        {{range $file, $findings := .FileFindings}}
        <div class="file-section">
            <div class="file-header">{{$file}}</div>
            {{range $findings}}
            <div class="finding severity-{{.Severity}}">
                <div>
                    <strong>{{.Message}}</strong>
                    <span class="rule-id">{{.RuleID}}</span>
                </div>
                <div class="location">Line {{.Line}}, Column {{.Column}}</div>
                {{if .Description}}
                <div class="description">{{.Description}}</div>
                {{end}}
            </div>
            {{end}}
        </div>
        {{end}}
    {{end}}
</body>
</html>
`