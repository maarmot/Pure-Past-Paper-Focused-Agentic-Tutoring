"""Check the distributable through its documented entry point, including dirty input."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/package_skill.py"


class RuntimePackageTests(unittest.TestCase):
    def test_only_manifest_blobs_at_the_selected_commit_are_packaged(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "source"
            repo.mkdir()

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo).decode().strip()

            git("init", "-q")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "user.name", "Synthetic fixture")
            git("config", "core.autocrlf", "false")
            (repo / "scripts").mkdir()
            shutil.copyfile(BUILDER, repo / "scripts/package_skill.py")
            (repo / "SKILL.md").write_bytes(b"committed instructions\n")
            (repo / "runtime-files.txt").write_bytes(b"SKILL.md\n")
            (repo / "hidden-note.txt").write_bytes(b"synthetic exclusion case")
            git("add", ".")
            git("commit", "-qm", "Original fixture")
            baseline = git("rev-parse", "HEAD")
            (repo / "SKILL.md").write_bytes(b"updated instructions\n")
            git("add", "SKILL.md")
            git("commit", "-qm", "Newer revision")
            (repo / "SKILL.md").write_bytes(b"dirty working bytes")
            (repo / "untracked.txt").write_bytes(b"untracked synthetic fixture")
            output = Path(temp) / "package.zip"

            def build(ref, destination=output):
                return subprocess.run(
                    [sys.executable, str(repo / "scripts/package_skill.py"), str(destination), "--ref", ref],
                    cwd=temp, capture_output=True, text=True
                )
            built = build(baseline)
            self.assertEqual(built.returncode, 0, built.stderr)
            self.assertEqual(json.loads(built.stdout)["commit"], baseline)
            with zipfile.ZipFile(output) as package:
                files = [entry for entry in package.namelist() if not entry.endswith("/")]
                self.assertEqual(files, ["ppp-learning/SKILL.md"])
                self.assertEqual(package.read(files[0]), b"committed instructions\n")
            original = output.read_bytes()
            self.assertNotEqual(build(baseline).returncode, 0)
            self.assertNotEqual(build("no-such-ref", Path(temp) / "absent.zip").returncode, 0)
            self.assertFalse((Path(temp) / "absent.zip").exists())
            self.assertEqual(output.read_bytes(), original)

            # Directory entries would silently widen the release to unrelated files.
            (repo / "runtime-files.txt").write_bytes(b"SKILL.md\nscripts\n")
            git("add", "runtime-files.txt")
            git("commit", "-qm", "Broken allowlist")
            broken = build("HEAD", Path(temp) / "broken.zip")
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn("regular file", broken.stderr)
            self.assertFalse((Path(temp) / "broken.zip").exists())
            self.assertEqual(output.read_bytes(), original)

    def test_runtime_manifest_covers_local_document_links_and_skill_metadata(self):
        manifest = set((ROOT / "runtime-files.txt").read_text(encoding="utf-8").splitlines())
        self.assertTrue({"SKILL.md", "agents/openai.yaml", "references/jane-street-license.txt",
                         "scripts/ppp_tools.py"}.issubset(manifest))
        for name in manifest:
            path = ROOT / name
            self.assertTrue(path.is_file(), name)
            self.assertFalse(name.startswith(("tests/", "examples/", "records/", ".git", "output/")))
            if path.suffix != ".md":
                continue
            for link in re.findall(r"\]\(([^)\n]+)\)", path.read_text(encoding="utf-8")):
                target = link.partition("#")[0]
                if target and "://" not in target and not target.startswith("mailto:"):
                    local = (path.parent / target.strip("<>")).resolve().relative_to(ROOT)
                    self.assertIn(local.as_posix(), manifest, name)
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        header = skill.split("---\n", 2)[1]
        self.assertRegex(header, r"(?m)^name: ppp-learning$")
        self.assertRegex(header, r"(?m)^description: .+")
        metadata = (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(metadata, r"(?m)^  default_prompt: .*\$ppp-learning")

    def test_substitution_cannot_change_packaged_instructions(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            def git(*args):
                subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)
            git("init", "-q")
            git("config", "core.autocrlf", "false")
            (repo / "scripts").mkdir()
            shutil.copyfile(BUILDER, repo / "scripts/package_skill.py")
            (repo / ".gitattributes").write_bytes(b"SKILL.md export-subst\n")
            (repo / "SKILL.md").write_bytes(b"Literal marker $Format:%H$\n")
            (repo / "runtime-files.txt").write_bytes(b"SKILL.md\n")
            git("add", ".")
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-qm", "Attribute fixture")
            result = subprocess.run([sys.executable, str(repo / "scripts/package_skill.py"),
                                     str(repo / "fixture.zip")], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("committed blob", result.stderr)
            self.assertFalse((repo / "fixture.zip").exists())
