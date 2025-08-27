package rules

import (
	"go/ast"
	"go/token"
	"strings"
	"unicode"

	"static-gate/pkg"
)

// NamingRule checks Go naming conventions
type NamingRule struct {
	BaseRule
}

func NewNamingRule() *NamingRule {
	return &NamingRule{
		BaseRule: BaseRule{
			id:          "naming.camelcase",
			name:        "Naming Conventions",
			description: "Enforces Go naming conventions (camelCase for unexported, PascalCase for exported)",
			severity:    pkg.SeverityWarning,
			category:    "naming",
		},
	}
}

func (r *NamingRule) Check(file *ast.File, fset *token.FileSet, filename string) []pkg.Finding {
	var findings []pkg.Finding

	ast.Inspect(file, func(n ast.Node) bool {
		switch node := n.(type) {
		case *ast.FuncDecl:
			if node.Name != nil && node.Name.IsExported() {
				if !r.isPascalCase(node.Name.Name) {
					pos := fset.Position(node.Pos())
					findings = append(findings, pkg.Finding{
						RuleID:      r.ID(),
						Message:     "Exported function should use PascalCase: " + node.Name.Name,
						Severity:    r.Severity(),
						File:        filename,
						Line:        pos.Line,
						Column:      pos.Column,
						Category:    r.Category(),
						Description: "Exported functions should follow PascalCase naming convention",
					})
				}
			} else if node.Name != nil && !node.Name.IsExported() {
				if !r.isCamelCase(node.Name.Name) {
					pos := fset.Position(node.Pos())
					findings = append(findings, pkg.Finding{
						RuleID:      r.ID(),
						Message:     "Unexported function should use camelCase: " + node.Name.Name,
						Severity:    r.Severity(),
						File:        filename,
						Line:        pos.Line,
						Column:      pos.Column,
						Category:    r.Category(),
						Description: "Unexported functions should follow camelCase naming convention",
					})
				}
			}
		case *ast.TypeSpec:
			if node.Name.IsExported() {
				if !r.isPascalCase(node.Name.Name) {
					pos := fset.Position(node.Pos())
					findings = append(findings, pkg.Finding{
						RuleID:      r.ID(),
						Message:     "Exported type should use PascalCase: " + node.Name.Name,
						Severity:    r.Severity(),
						File:        filename,
						Line:        pos.Line,
						Column:      pos.Column,
						Category:    r.Category(),
						Description: "Exported types should follow PascalCase naming convention",
					})
				}
			}
		case *ast.ValueSpec:
			for _, name := range node.Names {
				if name.IsExported() {
					if !r.isPascalCase(name.Name) {
						pos := fset.Position(name.Pos())
						findings = append(findings, pkg.Finding{
							RuleID:      r.ID(),
							Message:     "Exported variable should use PascalCase: " + name.Name,
							Severity:    r.Severity(),
							File:        filename,
							Line:        pos.Line,
							Column:      pos.Column,
							Category:    r.Category(),
							Description: "Exported variables should follow PascalCase naming convention",
						})
					}
				} else {
					if !r.isCamelCase(name.Name) {
						pos := fset.Position(name.Pos())
						findings = append(findings, pkg.Finding{
							RuleID:      r.ID(),
							Message:     "Unexported variable should use camelCase: " + name.Name,
							Severity:    r.Severity(),
							File:        filename,
							Line:        pos.Line,
							Column:      pos.Column,
							Category:    r.Category(),
							Description: "Unexported variables should follow camelCase naming convention",
						})
					}
				}
			}
		}
		return true
	})

	return findings
}

func (r *NamingRule) isPascalCase(name string) bool {
	if len(name) == 0 {
		return false
	}
	return unicode.IsUpper(rune(name[0])) && r.isValidIdentifier(name)
}

func (r *NamingRule) isCamelCase(name string) bool {
	if len(name) == 0 {
		return false
	}
	return unicode.IsLower(rune(name[0])) && r.isValidIdentifier(name)
}

func (r *NamingRule) isValidIdentifier(name string) bool {
	// Allow common Go patterns like underscores in certain contexts
	// This is a simplified check - could be made more sophisticated
	return !strings.Contains(name, "_") || strings.HasPrefix(name, "_")
}

// ImportRestrictionsRule checks for restricted imports
type ImportRestrictionsRule struct {
	BaseRule
	restrictedImports []string
}

func NewImportRestrictionsRule() *ImportRestrictionsRule {
	return &ImportRestrictionsRule{
		BaseRule: BaseRule{
			id:          "imports.restricted",
			name:        "Import Restrictions",
			description: "Checks for restricted or dangerous imports",
			severity:    pkg.SeverityWarning,
			category:    "imports",
		},
		restrictedImports: []string{
			"unsafe",           // Unsafe operations
			"reflect",          // Reflection can be dangerous
			"plugin",           // Dynamic loading
			"net/http/pprof",   // Profiling endpoint
		},
	}
}

func (r *ImportRestrictionsRule) Check(file *ast.File, fset *token.FileSet, filename string) []pkg.Finding {
	var findings []pkg.Finding

	for _, imp := range file.Imports {
		path := strings.Trim(imp.Path.Value, "\"")
		if r.isRestricted(path) {
			pos := fset.Position(imp.Pos())
			findings = append(findings, pkg.Finding{
				RuleID:      r.ID(),
				Message:     "Restricted import detected: " + path,
				Severity:    r.Severity(),
				File:        filename,
				Line:        pos.Line,
				Column:      pos.Column,
				Category:    r.Category(),
				Description: "Import of " + path + " is restricted due to potential security or safety concerns",
			})
		}
	}

	return findings
}

func (r *ImportRestrictionsRule) isRestricted(importPath string) bool {
	for _, restricted := range r.restrictedImports {
		if importPath == restricted || strings.HasPrefix(importPath, restricted+"/") {
			return true
		}
	}
	return false
}

// ComplexityRule checks for high cyclomatic complexity
type ComplexityRule struct {
	BaseRule
	maxComplexity int
}

func NewComplexityRule() *ComplexityRule {
	return &ComplexityRule{
		BaseRule: BaseRule{
			id:          "quality.complexity",
			name:        "Cyclomatic Complexity",
			description: "Checks for functions with high cyclomatic complexity",
			severity:    pkg.SeverityInfo,
			category:    "quality",
		},
		maxComplexity: 10,
	}
}

func (r *ComplexityRule) Check(file *ast.File, fset *token.FileSet, filename string) []pkg.Finding {
	var findings []pkg.Finding

	ast.Inspect(file, func(n ast.Node) bool {
		if fn, ok := n.(*ast.FuncDecl); ok && fn.Body != nil {
			complexity := r.calculateComplexity(fn.Body)
			if complexity > r.maxComplexity {
				pos := fset.Position(fn.Pos())
				findings = append(findings, pkg.Finding{
					RuleID:      r.ID(),
					Message:     "High cyclomatic complexity in function " + fn.Name.Name,
					Severity:    r.Severity(),
					File:        filename,
					Line:        pos.Line,
					Column:      pos.Column,
					Category:    r.Category(),
					Description: "Function has cyclomatic complexity of " + 
						string(rune(complexity+'0')) + " (max: " + string(rune(r.maxComplexity+'0')) + ")",
					Metadata: map[string]string{
						"complexity":     string(rune(complexity + '0')),
						"max_complexity": string(rune(r.maxComplexity + '0')),
						"function_name":  fn.Name.Name,
					},
				})
			}
		}
		return true
	})

	return findings
}

func (r *ComplexityRule) calculateComplexity(block *ast.BlockStmt) int {
	complexity := 1 // Base complexity

	ast.Inspect(block, func(n ast.Node) bool {
		switch n.(type) {
		case *ast.IfStmt:
			complexity++
		case *ast.ForStmt:
			complexity++
		case *ast.RangeStmt:
			complexity++
		case *ast.SwitchStmt:
			complexity++
		case *ast.TypeSwitchStmt:
			complexity++
		case *ast.CaseClause:
			// Don't double-count case clauses, they're part of switch complexity
		case *ast.CommClause:
			complexity++
		}
		return true
	})

	return complexity
}