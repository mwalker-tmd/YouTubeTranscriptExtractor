"""Core YouTube transcript extraction functionality."""

import re
import json
import requests
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter


class YouTubeTranscriptExtractor:
    """YouTube transcript extractor with timestamp support."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.formatter = JSONFormatter()
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """
        Extract video ID from various YouTube URL formats.
        
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID string
            
        Raises:
            ValueError: If video ID cannot be extracted
        """
        # Pattern for various YouTube URL formats
        pattern = r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})'
        
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Could not extract video ID from URL. Please check the URL format.")
    
    def get_transcript(self, video_id: str, language_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get transcript with timestamps for a given video ID.
        
        Args:
            video_id: YouTube video ID
            language_code: Optional language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            List of transcript entries with timestamps
            
        Raises:
            Exception: If transcript cannot be retrieved
        """
        try:
            if language_code:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = transcript_list.find_transcript([language_code])
                return transcript.fetch()
            else:
                return YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as e:
            raise Exception(f"Error getting transcript: {str(e)}")
    
    def get_available_languages(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get all available transcript languages for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of available languages with metadata
            
        Raises:
            Exception: If transcript list cannot be retrieved
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            languages = []
            for transcript in transcript_list:
                languages.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated
                })
            
            return languages
        except Exception as e:
            raise Exception(f"Error getting available languages: {str(e)}")
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """
        Convert seconds to HH:MM:SS format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def format_transcript_text(self, transcript: List[Dict[str, Any]]) -> str:
        """
        Format transcript as readable text with timestamps.
        
        Args:
            transcript: List of transcript entries
            
        Returns:
            Formatted transcript string
        """
        lines = []
        for entry in transcript:
            timestamp = self.format_timestamp(entry['start'])
            text = entry['text']
            lines.append(f"[{timestamp}] {text}")
        
        return '\n'.join(lines)
    
    def save_transcript_json(self, transcript: List[Dict[str, Any]], filename: str) -> None:
        """
        Save transcript to JSON file.
        
        Args:
            transcript: List of transcript entries
            filename: Output filename
        """
        json_transcript = self.formatter.format_transcript(transcript)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_transcript)
    
    def save_transcript_text(self, transcript: List[Dict[str, Any]], filename: str) -> None:
        """
        Save transcript to text file with timestamps.
        
        Args:
            transcript: List of transcript entries
            filename: Output filename
        """
        formatted_text = self.format_transcript_text(transcript)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
    
    def get_video_title(self, video_id: str) -> str:
        """
        Get the title of a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video title string
            
        Raises:
            Exception: If title cannot be retrieved
        """
        try:
            # Use YouTube's oEmbed API to get video info
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('title', f'video_{video_id}')
            
        except Exception as e:
            # Fallback to video ID if title can't be retrieved
            return f"video_{video_id}"
    
    @staticmethod
    def sanitize_filename(title: str) -> str:
        """
        Sanitize video title for use as filename.
        
        Args:
            title: Video title
            
        Returns:
            Sanitized filename with spaces replaced by dashes
        """
        # Replace spaces with dashes
        sanitized = title.replace(' ', '-')
        
        # Remove invalid filename characters
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '', sanitized)
        
        # Remove multiple consecutive dashes
        sanitized = re.sub(r'-+', '-', sanitized)
        
        # Remove leading/trailing dashes
        sanitized = sanitized.strip('-')
        
        # Limit length to avoid filesystem issues
        if len(sanitized) > 200:
            sanitized = sanitized[:200].rstrip('-')
        
        return sanitized or 'untitled'
    
    def extract_from_url(self, url: str, language_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract transcript directly from YouTube URL.
        
        Args:
            url: YouTube video URL
            language_code: Optional language code
            
        Returns:
            List of transcript entries with timestamps
        """
        video_id = self.extract_video_id(url)
        return self.get_transcript(video_id, language_code) 