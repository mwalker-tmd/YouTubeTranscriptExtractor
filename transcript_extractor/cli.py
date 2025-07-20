"""Command-line interface for YouTube transcript extractor."""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from .extractor import YouTubeTranscriptExtractor


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


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract transcripts from YouTube videos with timestamps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s https://youtu.be/dQw4w9WgXcQ --output transcript.txt
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ --language es --format json
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ --list-languages
        """
    )
    
    parser.add_argument(
        "url",
        help="YouTube video URL"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output filename (default: transcript_<video_id>.<format>)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "-l", "--language",
        help="Language code for transcript (e.g., en, es, fr)"
    )
    
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available languages for the video"
    )
    
    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Exclude timestamps from text output"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--conflict",
        choices=["prompt", "replace", "rename", "abort"],
        default="prompt",
        help="How to handle existing files (default: prompt)"
    )
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = YouTubeTranscriptExtractor()
    
    try:
        # Extract video ID
        if args.verbose:
            print(f"Extracting video ID from URL: {args.url}")
        
        video_id = extractor.extract_video_id(args.url)
        
        if args.verbose:
            print(f"Video ID: {video_id}")
        
        # List available languages if requested
        if args.list_languages:
            if args.verbose:
                print("Fetching available languages...")
            
            languages = extractor.get_available_languages(video_id)
            print("\nAvailable transcript languages:")
            print("=" * 40)
            
            for lang in languages:
                status = "(Auto-generated)" if lang['is_generated'] else "(Manual)"
                print(f"{lang['language']} ({lang['language_code']}) {status}")
            
            return
        
        # Get transcript
        if args.verbose:
            lang_msg = f" in {args.language}" if args.language else ""
            print(f"Retrieving transcript{lang_msg}...")
        
        transcript = extractor.get_transcript(video_id, args.language)
        
        if args.verbose:
            print(f"Retrieved {len(transcript)} transcript entries")
        
        # Get video title for filename
        if args.verbose:
            print("Fetching video title...")
        
        try:
            video_title = extractor.get_video_title(video_id)
            sanitized_title = extractor.sanitize_filename(video_title)
        except Exception:
            # Fallback to video ID if title fetch fails
            sanitized_title = f"video_{video_id}"
        
        if args.verbose:
            print(f"Video title: {video_title if 'video_title' in locals() else sanitized_title}")
        
        # Create transcripts directory
        transcripts_dir = Path("transcripts")
        transcripts_dir.mkdir(exist_ok=True)
        
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
        
        # Save transcript
        if args.format == "json":
            extractor.save_transcript_json(transcript, str(output_file))
        else:
            if args.no_timestamps:
                # Save plain text without timestamps
                plain_text = '\n'.join([entry['text'] for entry in transcript])
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(plain_text)
            else:
                extractor.save_transcript_text(transcript, str(output_file))
        
        print(f"Transcript saved to: {output_file}")
        
        # Display transcript preview if verbose
        if args.verbose:
            print(f"\nPreview (first 3 entries):")
            print("-" * 30)
            
            for i, entry in enumerate(transcript[:3]):
                timestamp = extractor.format_timestamp(entry['start'])
                print(f"[{timestamp}] {entry['text']}")
            
            if len(transcript) > 3:
                print(f"... and {len(transcript) - 3} more entries")
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nPossible reasons:", file=sys.stderr)
        print("- Video doesn't have captions/transcripts", file=sys.stderr)
        print("- Video is private or restricted", file=sys.stderr)
        print("- Invalid YouTube URL", file=sys.stderr)
        print("- Network connectivity issues", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 