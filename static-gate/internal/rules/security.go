package rules

import (
	"go/ast"
	"go/token"
	"strings"

	"static-gate/pkg"
)

// BaseRule provides common functionality for rules
type BaseRule struct {
	id          string
	name        string
	description string
	severity    pkg.Severity
	category    string
}

func (r *BaseRule) ID() string          { return r.id }
func (r *BaseRule) Name() string        { return r.name }
func (r *BaseRule) Description() string { return r.description }
func (r *BaseRule) Severity() pkg.Severity { return r.severity }
func (r *BaseRule) Category() string    { return r.category }

// DangerousExecRule checks for dangerous exec.Command usage
type DangerousExecRule struct {
	BaseRule
}

func NewDangerousExecRule() *DangerousExecRule {
	return &DangerousExecRule{
		BaseRule: BaseRule{
			id:          "security.dangerous-exec",
			name:        "Dangerous Exec Command",
			description: "Detects potentially dangerous exec.Command calls",
			severity:    pkg.SeverityError,
			category:    "security",
		},
	}
}

func (r *DangerousExecRule) Check(file *ast.File, fset *token.FileSet, filename string) []pkg.Finding {
	var findings []pkg.Finding

	ast.Inspect(file, func(n ast.Node) bool {
		if call, ok := n.(*ast.CallExpr); ok {
			if r.isDangerousExecCall(call) {
				pos := fset.Position(call.Pos())
				findings = append(findings, pkg.Finding{
					RuleID:   r.ID(),
					Message:  "Dangerous exec.Command call detected",
					Severity: r.Severity(),
					File:     filename,
					Line:     pos.Line,
					Column:   pos.Column,
					Category: r.Category(),
					Description: "exec.Command calls can be dangerous if user input is not properly sanitized",
				})
			}
		}
		return true
	})

	return findings
}

func (r *DangerousExecRule) isDangerousExecCall(call *ast.CallExpr) bool {
	if sel, ok := call.Fun.(*ast.SelectorExpr); ok {
		if pkg, ok := sel.X.(*ast.Ident); ok {
			return pkg.Name == "exec" && sel.Sel.Name == "Command"
		}
	}
	return false
}

// DangerousOSRule checks for dangerous OS operations
type DangerousOSRule struct {
	BaseRule
}

func NewDangerousOSRule() *DangerousOSRule {
	return &DangerousOSRule{
		BaseRule: BaseRule{
			id:          "security.dangerous-os",
			name:        "Dangerous OS Operations",
			description: "Detects potentially dangerous OS operations",
			severity:    pkg.SeverityError,
			category:    "security",
		},
	}
}

func (r *DangerousOSRule) Check(file *ast.File, fset *token.FileSet, filename string) []pkg.Finding {
	var findings []pkg.Finding
	dangerousOSFuncs := []string{"Remove", "RemoveAll", "Rename", "Chmod", "Chown"}

	ast.Inspect(file, func(n ast.Node) bool {
		if call, ok := n.(*ast.CallExpr); ok {
			if r.isDangerousOSCall(call, dangerousOSFuncs) {
				pos := fset.Position(call.Pos())
				funcName := r.getOSFunctionName(call)
				findings = append(findings, pkg.Finding{
					RuleID:   r.ID(),
					Message:  "Dangerous OS operation: " + funcName,
					Severity: r.Severity(),
					File:     filename,
					Line:     pos.Line,
					Column:   pos.Column,
					Category: r.Category(),
					Description: "OS operations like " + funcName + " can be dangerous if not properly controlled",
				})
			}
		}
		return true
	})

	return findings
}

func (r *DangerousOSRule) isDangerousOSCall(call *ast.CallExpr, dangerousFuncs []string) bool {
	if sel, ok := call.Fun.(*ast.SelectorExpr); ok {
		if pkg, ok := sel.X.(*ast.Ident); ok {
			if pkg.Name == "os" {
				for _, dangerous := range dangerousFuncs {
					if sel.Sel.Name == dangerous {
						return true
					}
				}
			}
		}
	}
	return false
}

func (r *DangerousOSRule) getOSFunctionName(call *ast.CallExpr) string {
	if sel, ok := call.Fun.(*ast.SelectorExpr); ok {
		return "os." + sel.Sel.Name
	}
	return "unknown"
}

// HardcodedSecretsRule checks for hardcoded secrets
type HardcodedSecretsRule struct {
	BaseRule
}

func NewHardcodedSecretsRule() *HardcodedSecretsRule {
	return &HardcodedSecretsRule{
		BaseRule: BaseRule{
			id:          "security.hardcoded-secrets",
			name:        "Hardcoded Secrets",
			description: "Detects hardcoded passwords, API keys, and other secrets",
			severity:    pkg.SeverityWarning,
			category:    "security",
		},
	}
}

func (r *HardcodedSecretsRule) Check(file *ast.File, fset *token.FileSet, filename string) []pkg.Finding {
	var findings []pkg.Finding
	suspiciousKeys := []string{"password", "passwd", "pwd", "secret", "key", "token", "api_key", "apikey"}

	ast.Inspect(file, func(n ast.Node) bool {
		switch node := n.(type) {
		case *ast.AssignStmt:
			r.checkAssignment(node, fset, filename, suspiciousKeys, &findings)
		case *ast.GenDecl:
			r.checkDeclaration(node, fset, filename, suspiciousKeys, &findings)
		}
		return true
	})

	return findings
}

func (r *HardcodedSecretsRule) checkAssignment(stmt *ast.AssignStmt, fset *token.FileSet, filename string, suspiciousKeys []string, findings *[]pkg.Finding) {
	for i, lhs := range stmt.Lhs {
		if ident, ok := lhs.(*ast.Ident); ok {
			if r.isSuspiciousKey(ident.Name, suspiciousKeys) && i < len(stmt.Rhs) {
				if r.isStringLiteral(stmt.Rhs[i]) {
					pos := fset.Position(stmt.Pos())
					*findings = append(*findings, pkg.Finding{
						RuleID:   r.ID(),
						Message:  "Potential hardcoded secret in variable: " + ident.Name,
						Severity: r.Severity(),
						File:     filename,
						Line:     pos.Line,
						Column:   pos.Column,
						Category: r.Category(),
						Description: "Hardcoded secrets should be replaced with environment variables or secure configuration",
					})
				}
			}
		}
	}
}

func (r *HardcodedSecretsRule) checkDeclaration(decl *ast.GenDecl, fset *token.FileSet, filename string, suspiciousKeys []string, findings *[]pkg.Finding) {
	for _, spec := range decl.Specs {
		if valueSpec, ok := spec.(*ast.ValueSpec); ok {
			for i, name := range valueSpec.Names {
				if r.isSuspiciousKey(name.Name, suspiciousKeys) && i < len(valueSpec.Values) {
					if r.isStringLiteral(valueSpec.Values[i]) {
						pos := fset.Position(valueSpec.Pos())
						*findings = append(*findings, pkg.Finding{
							RuleID:   r.ID(),
							Message:  "Potential hardcoded secret in variable: " + name.Name,
							Severity: r.Severity(),
							File:     filename,
							Line:     pos.Line,
							Column:   pos.Column,
							Category: r.Category(),
							Description: "Hardcoded secrets should be replaced with environment variables or secure configuration",
						})
					}
				}
			}
		}
	}
}

func (r *HardcodedSecretsRule) isSuspiciousKey(name string, suspiciousKeys []string) bool {
	lowerName := strings.ToLower(name)
	for _, key := range suspiciousKeys {
		if strings.Contains(lowerName, key) {
			return true
		}
	}
	return false
}

func (r *HardcodedSecretsRule) isStringLiteral(expr ast.Expr) bool {
	if lit, ok := expr.(*ast.BasicLit); ok {
		return lit.Kind.String() == "STRING" && len(lit.Value) > 2 // More than just quotes
	}
	return false
}