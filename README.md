# Subtitle Shift

Move every cue in a UTF-8 SRT file by a signed millisecond offset while preserving dialogue and line endings.

## Run

From this folder with Python 3.9 or later:

```sh
python main.py input.srt synced.srt --ms 1500
```

A cue starting at `00:00:02,000` moves to `00:00:03,500`. Negative offsets are supported if every resulting timestamp is at or after zero. Choose a new output filename.

## Limitations

Input must be UTF-8 SRT. An offset that moves a cue before zero is rejected.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and test commands, and the [changelog](CHANGELOG.md) for project history.

## License

[MIT License](LICENSE). Copyright (c) 2026 subtitle-shift contributors.
