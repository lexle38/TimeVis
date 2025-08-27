package main

import (
	"testing"
	
	"static-gate/internal/rules"
	"static-gate/internal/config"
	"static-gate/internal/analyzer"
)

func TestBasicFunctionality(t *testing.T) {
	// Test that we can create a configuration
	cfg := config.DefaultConfig()
	if cfg == nil {
		t.Fatal("Failed to create default configuration")
	}
	
	// Test that we can create a rules registry
	registry := rules.NewRegistry()
	if registry == nil {
		t.Fatal("Failed to create rules registry")
	}
	
	allRules := registry.GetAll()
	if len(allRules) == 0 {
		t.Fatal("No rules registered")
	}
	
	// Test that we can create an analyzer
	analyzer := analyzer.New(cfg, allRules)
	if analyzer == nil {
		t.Fatal("Failed to create analyzer")
	}
	
	t.Logf("Successfully created analyzer with %d rules", len(allRules))
}

func TestRuleRegistry(t *testing.T) {
	registry := rules.NewRegistry()
	
	// Check that expected rules are registered
	expectedRules := []string{
		"security.dangerous-exec",
		"security.dangerous-os", 
		"security.hardcoded-secrets",
		"naming.camelcase",
		"imports.restricted",
		"quality.complexity",
	}
	
	for _, ruleID := range expectedRules {
		rule, exists := registry.Get(ruleID)
		if !exists {
			t.Errorf("Rule %s not found in registry", ruleID)
		}
		if rule.ID() != ruleID {
			t.Errorf("Rule ID mismatch: expected %s, got %s", ruleID, rule.ID())
		}
	}
}

func TestConfigurationLoading(t *testing.T) {
	// Test default configuration
	cfg := config.DefaultConfig()
	
	if len(cfg.Rules) == 0 {
		t.Error("Default configuration has no rules")
	}
	
	if cfg.OutputFormat == "" {
		t.Error("Default configuration has no output format")
	}
	
	// Test that ignored directories are set
	if len(cfg.IgnoreDirs) == 0 {
		t.Error("Default configuration has no ignored directories")
	}
	
	expectedDirs := []string{"vendor", ".git", "node_modules"}
	for _, dir := range expectedDirs {
		found := false
		for _, ignored := range cfg.IgnoreDirs {
			if ignored == dir {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("Expected ignore directory '%s' not found", dir)
		}
	}
}