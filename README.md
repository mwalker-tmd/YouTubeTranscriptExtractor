# YouTube Transcript Extractor

A command-line tool for extracting transcripts from YouTube videos with timestamps.

## Features

- Extract transcripts from YouTube videos using the `youtube-transcript-api` library
- Support for multiple YouTube URL formats
- Timestamps included in transcript output
- Multiple output formats (text, JSON)
- Multi-language transcript support
- Command-line interface for automation
- Error handling for various edge cases

## Installation

This project uses `uv` for dependency management. To get started:

1. Install the package:
   ```bash
   uv sync
   ```

2. The tool will be available as `transcript-extractor` command

## Usage

### Basic Usage

Extract transcript from a YouTube video (saves to `transcripts/` folder with video title as filename):
```bash
uv run transcript-extractor "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Advanced Usage

```bash
# Save to specific file (in transcripts folder)
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --output my_transcript.txt

# Get transcript in JSON format (filename will be video-title.json)
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --format json

# Get transcript in specific language
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --language es

# List available languages
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --list-languages

# Get plain text without timestamps
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --no-timestamps

# Enable verbose output (shows video title and progress)
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --verbose

# Handle file conflicts automatically
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --conflict replace  # Overwrite existing
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --conflict rename   # Auto-create Video-Title(1).txt
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --conflict abort    # Cancel if file exists
```

### Command-line Options

- `--output`, `-o`: Output filename
- `--format`, `-f`: Output format (text or json)
- `--language`, `-l`: Language code (e.g., en, es, fr)
- `--list-languages`: Show available languages for the video
- `--no-timestamps`: Exclude timestamps from text output
- `--verbose`, `-v`: Enable verbose output
- `--conflict`: Handle file conflicts (prompt, replace, rename, abort)

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

## Dependencies

- `youtube-transcript-api` - For extracting YouTube transcripts
- `requests` - For fetching video titles

## Development

Install development dependencies:
```bash
uv sync --extra dev
```

This includes tools for code formatting, linting, and testing.

## Python API

You can also use the tool programmatically:

```python
from transcript_extractor import YouTubeTranscriptExtractor

extractor = YouTubeTranscriptExtractor()

# Extract from URL
transcript = extractor.extract_from_url("https://youtu.be/dQw4w9WgXcQ")

# Get available languages
languages = extractor.get_available_languages("dQw4w9WgXcQ")

# Save to file
extractor.save_transcript_text(transcript, "transcript.txt")
extractor.save_transcript_json(transcript, "transcript.json")
```

## License

MIT License 