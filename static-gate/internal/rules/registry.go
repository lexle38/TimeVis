package rules

import (
	"static-gate/pkg"
)

// Registry manages all available rules
type Registry struct {
	rules map[string]pkg.Rule
}

// NewRegistry creates a new rules registry
func NewRegistry() *Registry {
	registry := &Registry{
		rules: make(map[string]pkg.Rule),
	}
	
	// Register built-in rules
	registry.registerBuiltinRules()
	
	return registry
}

// registerBuiltinRules registers all built-in rules
func (r *Registry) registerBuiltinRules() {
	// Security rules
	r.Register(NewDangerousExecRule())
	r.Register(NewDangerousOSRule())
	r.Register(NewHardcodedSecretsRule())
	
	// Quality rules
	r.Register(NewNamingRule())
	r.Register(NewImportRestrictionsRule())
	r.Register(NewComplexityRule())
}

// Register adds a rule to the registry
func (r *Registry) Register(rule pkg.Rule) {
	r.rules[rule.ID()] = rule
}

// Get retrieves a rule by ID
func (r *Registry) Get(id string) (pkg.Rule, bool) {
	rule, exists := r.rules[id]
	return rule, exists
}

// GetAll returns all registered rules
func (r *Registry) GetAll() []pkg.Rule {
	rules := make([]pkg.Rule, 0, len(r.rules))
	for _, rule := range r.rules {
		rules = append(rules, rule)
	}
	return rules
}

// GetByCategory returns all rules in a specific category
func (r *Registry) GetByCategory(category string) []pkg.Rule {
	var rules []pkg.Rule
	for _, rule := range r.rules {
		if rule.Category() == category {
			rules = append(rules, rule)
		}
	}
	return rules
}

// ListRules returns a list of rule information
func (r *Registry) ListRules() []RuleInfo {
	var info []RuleInfo
	for _, rule := range r.rules {
		info = append(info, RuleInfo{
			ID:          rule.ID(),
			Name:        rule.Name(),
			Description: rule.Description(),
			Category:    rule.Category(),
			Severity:    rule.Severity(),
		})
	}
	return info
}

// RuleInfo provides information about a rule
type RuleInfo struct {
	ID          string       `json:"id"`
	Name        string       `json:"name"`
	Description string       `json:"description"`
	Category    string       `json:"category"`
	Severity    pkg.Severity `json:"severity"`
}