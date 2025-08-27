package example

import (
	"os"
	"os/exec"
	"unsafe"
)

// This file contains various code patterns that should trigger rules

const (
	// Hardcoded secrets - should trigger security.hardcoded-secrets
	APIKey    = "sk-1234567890abcdef"
	password  = "secret123"
	dbToken   = "token-abcd1234"
)

// bad_function_name violates naming conventions - should trigger naming.camelcase
func bad_function_name() {
	// Dangerous exec call - should trigger security.dangerous-exec
	cmd := exec.Command("rm", "-rf", "/tmp/*")
	cmd.Run()
}

// ExportedFunc should use PascalCase but is correct
func ExportedFunc() {
	// Dangerous OS operations - should trigger security.dangerous-os
	os.Remove("/important/file.txt")
	os.RemoveAll("/some/directory")
	
	// Using unsafe - should trigger imports.restricted
	var ptr *int
	uintptr(unsafe.Pointer(ptr))
}

// complexFunction has high cyclomatic complexity - should trigger quality.complexity
func complexFunction(x int) int {
	if x > 0 {
		if x > 10 {
			if x > 20 {
				if x > 30 {
					if x > 40 {
						if x > 50 {
							return x * 2
						} else {
							return x * 3
						}
					} else {
						return x * 4
					}
				} else {
					return x * 5
				}
			} else {
				return x * 6
			}
		} else {
			return x * 7
		}
	} else {
		return x * 8
	}
}

// This is a properly named unexported function
func properFunction() {
	// This is clean code
	println("Hello, World!")
}