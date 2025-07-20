# File Conflict Handling Feature Patch

This file contains the changes for implementing file conflict handling that were temporarily rolled back.

## Changes to apply later:

### 1. transcript_extractor/cli.py additions:

Add these imports:
```python
from datetime import datetime
```

Add this argument to the parser:
```python
parser.add_argument(
    "--conflict",
    choices=["prompt", "replace", "rename", "abort"],
    default="prompt",
    help="How to handle existing files (default: prompt)"
)
```

Add these two functions before `main()`:
```python
def handle_file_conflict(file_path: Path, conflict_mode: str) -> Optional[Path]:
    """
    Handle file conflicts when output file already exists.
    
    Args:
        file_path: The intended output file path
        conflict_mode: How to handle conflicts ('prompt', 'replace', 'rename', 'abort')
        
    Returns:
        Path to use for output, or None if user chooses to abort
    """
    if not file_path.exists():
        return file_path
    
    if conflict_mode == "replace":
        return file_path
    
    elif conflict_mode == "abort":
        return None
    
    elif conflict_mode == "rename":
        return get_unique_filename(file_path)
    
    elif conflict_mode == "prompt":
        print(f"\nFile already exists: {file_path}")
        while True:
            choice = input("(R)eplace, (C)reate new, or (A)bort? [R/C/A]: ").strip().upper()
            
            if choice in ['R', 'REPLACE']:
                return file_path
            elif choice in ['C', 'CREATE']:
                return get_unique_filename(file_path)
            elif choice in ['A', 'ABORT']:
                return None
            else:
                print("Please enter R, C, or A")
    
    return file_path


def get_unique_filename(file_path: Path) -> Path:
    """
    Generate a unique filename by adding a suffix.
    
    Args:
        file_path: Original file path
        
    Returns:
        Unique file path with suffix
    """
    stem = file_path.stem
    suffix = file_path.suffix
    parent = file_path.parent
    
    counter = 1
    while True:
        new_path = parent / f"{stem}({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
```

Replace the output file handling section in `main()`:
```python
# REPLACE THIS SECTION:
# Determine output filename
if args.output:
    # If user specifies output, still put it in transcripts folder unless it's an absolute path
    if os.path.isabs(args.output):
        output_file = args.output
    else:
        output_file = transcripts_dir / args.output
else:
    extension = "json" if args.format == "json" else "txt"
    output_file = transcripts_dir / f"{sanitized_title}.{extension}"

# WITH THIS:
# Determine output filename
if args.output:
    # If user specifies output, still put it in transcripts folder unless it's an absolute path
    if os.path.isabs(args.output):
        intended_output = Path(args.output)
    else:
        intended_output = transcripts_dir / args.output
else:
    extension = "json" if args.format == "json" else "txt"
    intended_output = transcripts_dir / f"{sanitized_title}.{extension}"

# Handle file conflicts
output_file = handle_file_conflict(intended_output, args.conflict)
if output_file is None:
    print("Operation aborted.")
    return

if output_file != intended_output and args.verbose:
    print(f"Using filename: {output_file}")
```

### 2. README.md additions:

Add to command-line options:
```markdown
- `--conflict`: Handle file conflicts (prompt, replace, rename, abort)
```

Add these examples:
```bash
# Handle file conflicts automatically
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --conflict replace  # Overwrite existing
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --conflict rename   # Auto-create Video-Title(1).txt
uv run transcript-extractor "https://youtu.be/dQw4w9WgXcQ" --conflict abort    # Cancel if file exists
```

## Testing scenarios to implement:

1. Test file conflict prompt with R/C/A choices
2. Test --conflict replace mode
3. Test --conflict rename mode (multiple files)
4. Test --conflict abort mode
5. Test conflict handling with custom output paths
6. Test conflict handling with absolute paths 