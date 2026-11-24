from pathlib import Path

import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args, code=0):
    script = next(ROOT.glob("*.py"))
    result = subprocess.run(
        [sys.executable, "-B", str(script), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=dict(os.environ, PYTHONUTF8="1"),
    )
    assert result.returncode == code, result.stderr
    return result.stdout


with tempfile.TemporaryDirectory() as temp:
    base = Path(temp)
    source = base / "sub.srt"
    source.write_bytes(b"1\r\n00:00:02,000 --> 00:00:03,000\r\nHello\r\n")
    shifted = base / "new.srt"
    run(source, shifted, "--ms", 1500)
    assert shifted.read_bytes() == b"1\r\n00:00:03,500 --> 00:00:04,500\r\nHello\r\n"
    run(source, base / "bad.srt", "--ms", -3000, code=1)
