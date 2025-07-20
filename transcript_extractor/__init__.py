"""YouTube Transcript Extractor

A Python package for extracting transcripts from YouTube videos with timestamps.
"""

__version__ = "0.1.0"
__author__ = "User"

from .extractor import YouTubeTranscriptExtractor
from .cli import main

__all__ = ["YouTubeTranscriptExtractor", "main"] 