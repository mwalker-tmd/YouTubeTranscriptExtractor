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

- `--output`, `-o`: Output filename (relative paths use transcripts folder, absolute paths used directly)
- `--format`, `-f`: Output format (text or json, default: text)
- `--language`, `-l`: Language code for transcript (e.g., en, es, fr, de)
- `--list-languages`: Show available languages for the video (doesn't extract transcript)
- `--no-timestamps`: Exclude timestamps from text output (plain text only)
- `--verbose`, `-v`: Enable verbose output (shows video title, progress, and debug info)
- `--conflict`: Handle file conflicts when output file exists:
  - `prompt` (default): Interactive prompts to Replace/Create/Abort
  - `replace`: Always overwrite existing files
  - `rename`: Auto-generate unique filenames with (1), (2), etc.
  - `abort`: Cancel operation if file already exists

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

## Dependencies

- `youtube-transcript-api` - For extracting YouTube transcripts
- `requests` - For fetching video titles

## Development

### Install Development Dependencies

Install all development tools including testing, linting, and formatting:
```bash
uv sync --extra dev
```

This includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `mypy` - Type checking

### Running Tests

Run the full test suite with coverage:
```bash
uv run pytest
```

Run tests with verbose output:
```bash
uv run pytest -v
```

Run specific test file:
```bash
uv run pytest tests/test_extractor.py
```

### Code Quality

Format code with black:
```bash
uv run black transcript_extractor/ tests/
```

Sort imports:
```bash
uv run isort transcript_extractor/ tests/
```

Run linting:
```bash
uv run flake8 transcript_extractor/ tests/
```

Type checking:
```bash
uv run mypy transcript_extractor/
```

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

## All Available Commands

### Project Setup
```bash
# Install project dependencies
uv sync

# Install with development tools
uv sync --extra dev
```

### Transcript Extraction
```bash
# Basic extraction
uv run transcript-extractor "YOUTUBE_URL"

# With all common options
uv run transcript-extractor "URL" --output "filename.txt" --format text --language en --verbose

# JSON format with conflict handling
uv run transcript-extractor "URL" --format json --conflict rename

# List available languages only
uv run transcript-extractor "URL" --list-languages

# Plain text without timestamps
uv run transcript-extractor "URL" --no-timestamps
```

### Development & Testing
```bash
# Run all tests with coverage
uv run pytest

# Run tests with verbose output  
uv run pytest -v

# Run specific test file
uv run pytest tests/test_extractor.py

# Run specific test function
uv run pytest tests/test_cli.py::TestCLI::test_basic_extraction
```

### Code Quality
```bash
# Format all code
uv run black transcript_extractor/ tests/

# Sort imports
uv run isort transcript_extractor/ tests/

# Check code style
uv run flake8 transcript_extractor/ tests/

# Type checking
uv run mypy transcript_extractor/
```

### Package Management
```bash
# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update dependencies
uv sync

# Show dependency tree
uv tree
```

## License

MIT License 