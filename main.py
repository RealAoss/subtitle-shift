import argparse
import re
from pathlib import Path

stamp = r"\d{2,}:[0-5]\d:[0-5]\d,\d{3}"
timing = re.compile(rf"({stamp})([ \t]+-->[ \t]+)({stamp})([^\r\n]*)")

def milliseconds(value):
    h, m, s, ms = map(int, re.split("[:,]", value))
    return ((h * 60 + m) * 60 + s) * 1000 + ms

def shifted(value, offset):
    total = milliseconds(value) + offset
    if total < 0:
        raise ValueError("Offset would create a negative timestamp")
    seconds, ms = divmod(total, 1000)
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    return f"{hours:02}:{minute:02}:{sec:02},{ms:03}"

parser = argparse.ArgumentParser(description="Shift SRT timestamps in milliseconds")
parser.add_argument("source", type=Path)
parser.add_argument("target", type=Path)
parser.add_argument("--ms", required=True, type=int)
args = parser.parse_args()
try:
    raw = args.source.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    lines = raw.decode(encoding).splitlines(keepends=True)
    block_start = True
    count = 0
    for index, line in enumerate(lines):
        if not line.strip():
            block_start = True
            continue
        if not block_start:
            continue
        block_start = False
        pos = index + int(line.strip().isdigit())
        content = lines[pos].rstrip("\r\n") if pos < len(lines) else ""
        match = timing.fullmatch(content)
        if not match:
            raise ValueError(f"Invalid cue at line {index + 1}")
        start, arrow, end, extra = match.groups()
        if milliseconds(end) < milliseconds(start):
            raise ValueError(f"Reversed cue at line {pos + 1}")
        lines[pos] = (shifted(start, args.ms) + arrow + shifted(end, args.ms)
                      + extra + lines[pos][len(content):])
        count += 1
    if not count:
        raise ValueError("No cues found")
    with args.target.open("xb") as output:
        output.write("".join(lines).encode(encoding))
except (ValueError, OSError) as error:
    parser.exit(1, f"{error}\n")
