package utils

import (
	"go/token"
	"os"
	"path/filepath"
	"strings"
)

// IsGoFile checks if a file is a Go source file
func IsGoFile(filename string) bool {
	return strings.HasSuffix(filename, ".go")
}

// GetRelativePath returns the relative path from a base directory
func GetRelativePath(basePath, fullPath string) string {
	rel, err := filepath.Rel(basePath, fullPath)
	if err != nil {
		return fullPath
	}
	return rel
}

// FileExists checks if a file exists
func FileExists(filename string) bool {
	_, err := os.Stat(filename)
	return !os.IsNotExist(err)
}

// FormatPosition formats a token position for display
func FormatPosition(pos token.Position) string {
	return pos.String()
}

// EnsureDirectory creates a directory if it doesn't exist
func EnsureDirectory(dir string) error {
	return os.MkdirAll(dir, 0755)
}

// GetFileSize returns the size of a file in bytes
func GetFileSize(filename string) (int64, error) {
	info, err := os.Stat(filename)
	if err != nil {
		return 0, err
	}
	return info.Size(), nil
}

// IsHidden checks if a file or directory is hidden (starts with .)
func IsHidden(name string) bool {
	return strings.HasPrefix(filepath.Base(name), ".")
}

// SplitPath splits a file path into directory and filename
func SplitPath(path string) (dir, file string) {
	return filepath.Split(path)
}

// JoinPath joins path elements
func JoinPath(elements ...string) string {
	return filepath.Join(elements...)
}

// NormalizePath normalizes a file path
func NormalizePath(path string) string {
	return filepath.Clean(path)
}