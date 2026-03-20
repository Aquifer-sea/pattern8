"""
P8 Tests — CLI tools and SKILL validation tests.

Tests focus on CLI commands and SKILL file integrity.
"""

import subprocess
import sys
from pathlib import Path

import pytest


# ════════════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════════════

def run_p8(*args: str) -> subprocess.CompletedProcess:
    """Run a p8 CLI command."""
    result = subprocess.run(
        [sys.executable, "-m", "p8.cli", *args],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
    )
    # Normalize output attribute
    result.output = result.stdout + result.stderr
    return result



# ════════════════════════════════════════════════════════════
#  SKILL File Integrity Tests
# ════════════════════════════════════════════════════════════

class TestSkillIntegrity:
    """Test built-in SKILL integrity."""

    SKILLS_DIR = Path(__file__).parent.parent / "skills"
    EXPECTED_SKILLS = ["example", "code_review", "bug_fix", "refactor", "feature_dev"]

    def test_all_skills_exist(self):
        """All expected SKILL directories exist."""
        for name in self.EXPECTED_SKILLS:
            assert (self.SKILLS_DIR / name).is_dir(), f"SKILL directory missing: {name}"

    def test_all_skills_have_skill_md(self):
        """Each SKILL has SKILL.md."""
        for name in self.EXPECTED_SKILLS:
            assert (self.SKILLS_DIR / name / "SKILL.md").is_file(), f"SKILL.md missing: {name}"

    def test_all_skills_have_checklist(self):
        """Each SKILL has checklist.yaml."""
        for name in self.EXPECTED_SKILLS:
            assert (self.SKILLS_DIR / name / "assets" / "checklist.yaml").is_file(), f"checklist missing: {name}"

    def test_all_skills_have_template(self):
        """Each SKILL has template.yaml."""
        for name in self.EXPECTED_SKILLS:
            assert (self.SKILLS_DIR / name / "assets" / "template.yaml").is_file(), f"template missing: {name}"

    def test_all_skills_have_guidelines(self):
        """Each SKILL has guidelines.yaml."""
        for name in self.EXPECTED_SKILLS:
            assert (self.SKILLS_DIR / name / "references" / "guidelines.yaml").is_file(), f"guidelines missing: {name}"

    def test_all_skills_have_security(self):
        """Each SKILL has security.yaml."""
        for name in self.EXPECTED_SKILLS:
            assert (self.SKILLS_DIR / name / "references" / "security.yaml").is_file(), f"security missing: {name}"

    def test_skill_md_has_frontmatter(self):
        """SKILL.md contains frontmatter metadata."""
        import frontmatter
        for name in self.EXPECTED_SKILLS:
            post = frontmatter.load(str(self.SKILLS_DIR / name / "SKILL.md"))
            assert post.metadata.get("name"), f"{name}/SKILL.md missing 'name' field"
            assert post.metadata.get("description"), f"{name}/SKILL.md missing 'description'"
            assert post.metadata.get("assets"), f"{name}/SKILL.md missing 'assets' config"

    def test_skill_md_has_pipeline(self):
        """SKILL.md contains <PIPELINE> tags."""
        for name in self.EXPECTED_SKILLS:
            content = (self.SKILLS_DIR / name / "SKILL.md").read_text()
            assert "<PIPELINE>" in content, f"{name}/SKILL.md missing <PIPELINE> tag"
            assert "</PIPELINE>" in content, f"{name}/SKILL.md missing </PIPELINE> tag"

    def test_skill_md_has_hard_gate(self):
        """SKILL.md contains <HARD-GATE> tags."""
        for name in self.EXPECTED_SKILLS:
            content = (self.SKILLS_DIR / name / "SKILL.md").read_text()
            assert "<HARD-GATE>" in content, f"{name}/SKILL.md missing <HARD-GATE> tag"

    def test_checklist_yaml_valid(self):
        """checklist.yaml is valid YAML."""
        import yaml
        for name in self.EXPECTED_SKILLS:
            with open(self.SKILLS_DIR / name / "assets" / "checklist.yaml") as f:
                data = yaml.safe_load(f)
            assert "checklist" in data, f"{name}/checklist.yaml missing 'checklist' field"
            assert len(data["checklist"]) > 0, f"{name}/checklist.yaml has empty checklist"

    def test_template_yaml_valid(self):
        """template.yaml is valid YAML."""
        import yaml
        for name in self.EXPECTED_SKILLS:
            with open(self.SKILLS_DIR / name / "assets" / "template.yaml") as f:
                data = yaml.safe_load(f)
            assert "template" in data, f"{name}/template.yaml missing 'template' field"

    def test_guidelines_yaml_valid(self):
        """guidelines.yaml is valid YAML."""
        import yaml
        for name in self.EXPECTED_SKILLS:
            with open(self.SKILLS_DIR / name / "references" / "guidelines.yaml") as f:
                data = yaml.safe_load(f)
            assert "guidelines" in data, f"{name}/guidelines.yaml missing 'guidelines' field"

    def test_security_yaml_valid(self):
        """security.yaml is valid YAML."""
        import yaml
        for name in self.EXPECTED_SKILLS:
            with open(self.SKILLS_DIR / name / "references" / "security.yaml") as f:
                data = yaml.safe_load(f)
            assert "security" in data, f"{name}/security.yaml missing 'security' field"


# ════════════════════════════════════════════════════════════
#  CLI Command Tests
# ════════════════════════════════════════════════════════════

class TestCLI:
    """Test CLI commands."""

    def test_help(self):
        """p8 --help works."""
        result = run_p8("--help")
        assert result.returncode == 0
        assert "Pattern 8" in result.output or "P8" in result.output

    def test_list(self):
        """p8 list shows 5 skills."""
        result = run_p8("list")
        assert result.returncode == 0
        assert "code_review" in result.output
        assert "bug_fix" in result.output
        assert "Total: 5" in result.output

    def test_validate_code_review(self):
        """p8 validate passes."""
        result = run_p8("validate", "skills/code_review")
        assert result.returncode == 0
        assert "All checks passed" in result.output

    def test_validate_all_skills(self):
        """All SKILLs pass validate."""
        for name in TestSkillIntegrity.EXPECTED_SKILLS:
            result = run_p8("validate", f"skills/{name}")
            assert result.returncode == 0, f"SKILL {name} validation failed: {result.output}"

    def test_new_and_validate(self, tmp_path):
        """p8 new creates a valid SKILL."""
        result = run_p8("new", "test_skill", "--dir", str(tmp_path))
        assert result.returncode == 0
        assert "SKILL created" in result.output

        # New SKILL should pass validation
        result = run_p8("validate", str(tmp_path / "test_skill"))
        assert result.returncode == 0


# ════════════════════════════════════════════════════════════
#  AGENTS.md Tests
# ════════════════════════════════════════════════════════════

class TestAgentsMd:
    """Test AGENTS.md global instruction file."""

    AGENTS_PATH = Path(__file__).parent.parent / "AGENTS.md"

    def test_agents_md_exists(self):
        """AGENTS.md exists."""
        assert self.AGENTS_PATH.is_file()

    def test_contains_five_patterns(self):
        """Contains 5 patterns."""
        content = self.AGENTS_PATH.read_text()
        patterns = ["Pipeline", "Inversion", "Generator", "Tool Wrapper", "Reviewer"]
        for p in patterns:
            assert p in content, f"AGENTS.md missing pattern: {p}"

    def test_contains_security_instructions(self):
        """Contains security red line instructions."""
        content = self.AGENTS_PATH.read_text()
        assert "security" in content.lower()
