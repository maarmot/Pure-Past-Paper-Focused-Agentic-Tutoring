"""Make a Codex skill ZIP from the exact files listed in a Git commit."""
import argparse
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ppp-learning/"


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def package(ref, output):
    commit = git("rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()
    names = git("show", commit + ":runtime-files.txt").decode("utf-8").splitlines()
    entries = git("ls-tree", "-rz", commit).decode("utf-8").split("\0")
    blobs = {}
    for entry in filter(None, entries):
        header, name = entry.split("\t", 1)
        mode, _, oid = header.split()
        if mode in {"100644", "100755"}:
            blobs[name] = oid
    if "SKILL.md" not in names or len(names) != len(set(names)):
        raise ValueError("Runtime manifest needs SKILL.md and unique paths")
    for name in names:
        parts = PurePosixPath(name).parts
        if (name not in blobs or not parts
                or any(part in {".", "..", "/"} for part in parts)
                or "\\" in name or ":" in name):
            raise ValueError("Expected a tracked regular file in the manifest: " + name)
    data = git("--literal-pathspecs", "archive", "--format=zip", "--prefix=" + PREFIX,
               commit, "--", *names)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        files = [entry for entry in archive.infolist() if not entry.is_dir()]
        if sorted(e.filename for e in files) != sorted(PREFIX + n for n in names):
            raise ValueError("Git archive contents differ from the runtime manifest")
        for entry in files:
            name = entry.filename[len(PREFIX):]
            oid = blobs[name]
            digest = hashlib.new("sha256" if len(oid) == 64 else "sha1")
            digest.update(f"blob {entry.file_size}\0".encode("ascii"))
            digest.update(archive.read(entry))
            if digest.hexdigest() != oid:
                raise ValueError("Archived file differs from the committed blob: " + name)
        size = sum(e.file_size for e in files)
    with output.open("xb") as dest:
        try:
            dest.write(data)
        except OSError:
            dest.close()
            output.unlink()
            raise
    return {"commit": commit, "files": len(names), "uncompressed_bytes": size,
            "zip_bytes": len(data), "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new output ZIP path")
    parser.add_argument("--ref", default="HEAD", help="local Git revision (default HEAD)")
    args = parser.parse_args()
    try:
        report = package(args.ref, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
