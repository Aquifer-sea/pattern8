# Changelog

All notable changes to this project will be documented in this file.

## [0.2.2] - 2025-03-20

### Fixed
- Lowered `requires-python` to `>=3.8` for maximum compatibility
- Users on conda/system Python can now `pip install pattern8` without errors

## [0.2.1] - 2025-03-20

### Fixed
- Lowered `requires-python` from `>=3.11` to `>=3.9`

## [0.2.0] - 2025-03-20

### Added
- 🎱 Initial public release
- 5 built-in SKILLs: `example`, `code_review`, `bug_fix`, `feature_dev`, `refactor`
- CLI tool: `p8 init`, `p8 list`, `p8 validate`, `p8 new`, `p8 serve`, `p8 mcp-config`
- MCP enforcement server with 2 tools: `submit_review`, `execute_tool`
- SecurityGuard — regex blacklist + path restrictions + write protection
- Reviewer — pure Python static audit engine (5 rule types, zero API key)
- Git pre-commit hook for commit-time SKILL integrity checks
- Cursor Rules (`.cursor/rules/p8-enforcement.mdc`) for IDE enforcement
- `AGENTS.md` global Agent instruction file
- 59 tests covering all enforcement modules and CLI commands
- Full English codebase and documentation
