"""Run one packet in a fresh Codex CLI process. Run with a logged-in Codex CLI supporting these flags."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

def run(packet_path, output_path, work_dir):
    executable = shutil.which("codex")
    if not executable:
        raise SystemExit("Codex CLI not found")
    cmd = [executable, "exec", "--ignore-user-config", "--ephemeral", "-s", "read-only",
           "-C", str(work_dir), "--skip-git-repo-check", "--json", "-o", str(output_path), "-"]
    start = time.perf_counter()
    process = subprocess.run(cmd, input=packet_path.read_bytes(), capture_output=True, timeout=300)
    elapsed = time.perf_counter() - start
    if process.returncode:
        raise RuntimeError(f"codex exec failed with exit status {process.returncode}; no result counted")
    events = [json.loads(line) for line in process.stdout.splitlines() if line.strip().startswith(b"{")]
    completed = [event for event in events if event.get("type") == "turn.completed"]
    external = [e["item"]["type"] for e in events if e.get("type") == "item.completed"
                and e["item"]["type"] not in {"agent_message", "reasoning"}]
    if len(completed) != 1 or external:
        raise RuntimeError(f"Unexpected turn count or tool use: {len(completed)}, {external}")
    stats = {"cli": subprocess.check_output([executable, "--version"], text=True).strip(),
             "seconds": round(elapsed, 2), "usage": completed[0]["usage"], "observed_tool_calls": external,
             "seed_temperature": "host defaults, not exposed", "model": "CLI defaults; model ID not present in completion events",
             "billing": "not reported"}
    output_path.with_suffix(".metrics.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(output_path.name, stats["seconds"])

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("packet", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("neutral", type=Path)
    a=p.parse_args()
    run(a.packet.resolve(), a.output.resolve(), a.neutral.resolve())
