"""Tests for the YouTube transcript extractor."""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from transcript_extractor.extractor import YouTubeTranscriptExtractor


class TestYouTubeTranscriptExtractor:
    """Test cases for YouTubeTranscriptExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = YouTubeTranscriptExtractor()
        self.sample_transcript = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.5},
            {'text': 'This is a test', 'start': 2.5, 'duration': 3.0},
            {'text': 'YouTube transcript', 'start': 5.5, 'duration': 2.0}
        ]
    
    def test_extract_video_id_standard_url(self):
        """Test video ID extraction from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self):
        """Test video ID extraction from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test video ID extraction from embed YouTube URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_v_url(self):
        """Test video ID extraction from /v/ YouTube URL."""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_with_parameters(self):
        """Test video ID extraction with additional URL parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=abc123"
        result = self.extractor.extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test video ID extraction with invalid URL."""
        url = "https://www.example.com/not-a-youtube-url"
        with pytest.raises(ValueError, match="Could not extract video ID"):
            self.extractor.extract_video_id(url)
    
    def test_extract_video_id_empty_url(self):
        """Test video ID extraction with empty URL."""
        url = ""
        with pytest.raises(ValueError, match="Could not extract video ID"):
            self.extractor.extract_video_id(url)
    
    @patch('transcript_extractor.extractor.YouTubeTranscriptApi.get_transcript')
    def test_get_transcript_success(self, mock_get_transcript):
        """Test successful transcript retrieval."""
        mock_get_transcript.return_value = self.sample_transcript
        
        result = self.extractor.get_transcript("dQw4w9WgXcQ")
        
        assert result == self.sample_transcript
        mock_get_transcript.assert_called_once_with("dQw4w9WgXcQ")
    
    @patch('transcript_extractor.extractor.YouTubeTranscriptApi.get_transcript')
    def test_get_transcript_failure(self, mock_get_transcript):
        """Test transcript retrieval failure."""
        mock_get_transcript.side_effect = Exception("Transcript not available")
        
        with pytest.raises(Exception, match="Error getting transcript"):
            self.extractor.get_transcript("invalid_id")
    
    @patch('transcript_extractor.extractor.YouTubeTranscriptApi.list_transcripts')
    def test_get_transcript_with_language(self, mock_list_transcripts):
        """Test transcript retrieval with specific language."""
        mock_transcript_list = Mock()
        mock_transcript = Mock()
        mock_transcript.fetch.return_value = self.sample_transcript
        mock_transcript_list.find_transcript.return_value = mock_transcript
        mock_list_transcripts.return_value = mock_transcript_list
        
        result = self.extractor.get_transcript("dQw4w9WgXcQ", "es")
        
        assert result == self.sample_transcript
        mock_list_transcripts.assert_called_once_with("dQw4w9WgXcQ")
        mock_transcript_list.find_transcript.assert_called_once_with(["es"])
        mock_transcript.fetch.assert_called_once()
    
    @patch('transcript_extractor.extractor.YouTubeTranscriptApi.list_transcripts')
    def test_get_available_languages_success(self, mock_list_transcripts):
        """Test successful language list retrieval."""
        mock_transcript1 = Mock()
        mock_transcript1.language = "English"
        mock_transcript1.language_code = "en"
        mock_transcript1.is_generated = False
        
        mock_transcript2 = Mock()
        mock_transcript2.language = "Spanish"
        mock_transcript2.language_code = "es"
        mock_transcript2.is_generated = True
        
        mock_list_transcripts.return_value = [mock_transcript1, mock_transcript2]
        
        result = self.extractor.get_available_languages("dQw4w9WgXcQ")
        
        expected = [
            {'language': 'English', 'language_code': 'en', 'is_generated': False},
            {'language': 'Spanish', 'language_code': 'es', 'is_generated': True}
        ]
        assert result == expected
    
    @patch('transcript_extractor.extractor.YouTubeTranscriptApi.list_transcripts')
    def test_get_available_languages_failure(self, mock_list_transcripts):
        """Test language list retrieval failure."""
        mock_list_transcripts.side_effect = Exception("Could not list transcripts")
        
        with pytest.raises(Exception, match="Error getting available languages"):
            self.extractor.get_available_languages("invalid_id")
    
    def test_format_timestamp_with_hours(self):
        """Test timestamp formatting with hours."""
        result = self.extractor.format_timestamp(3661.5)  # 1 hour, 1 minute, 1 second
        assert result == "01:01:01"
    
    def test_format_timestamp_without_hours(self):
        """Test timestamp formatting without hours."""
        result = self.extractor.format_timestamp(61.5)  # 1 minute, 1 second
        assert result == "01:01"
    
    def test_format_timestamp_zero(self):
        """Test timestamp formatting with zero."""
        result = self.extractor.format_timestamp(0)
        assert result == "00:00"
    
    def test_format_transcript_text(self):
        """Test transcript text formatting with timestamps."""
        result = self.extractor.format_transcript_text(self.sample_transcript)
        
        expected_lines = [
            "[00:00] Hello world",
            "[00:02] This is a test", 
            "[00:05] YouTube transcript"
        ]
        expected = '\n'.join(expected_lines)
        
        assert result == expected
    
    def test_format_transcript_text_empty(self):
        """Test transcript text formatting with empty transcript."""
        result = self.extractor.format_transcript_text([])
        assert result == ""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('transcript_extractor.extractor.JSONFormatter')
    def test_save_transcript_json(self, mock_formatter_class, mock_file):
        """Test saving transcript to JSON file."""
        mock_formatter = Mock()
        mock_formatter.format_transcript.return_value = '{"test": "json"}'
        mock_formatter_class.return_value = mock_formatter
        
        # Create new extractor to use the mocked formatter
        extractor = YouTubeTranscriptExtractor()
        extractor.save_transcript_json(self.sample_transcript, "test.json")
        
        mock_file.assert_called_once_with("test.json", 'w', encoding='utf-8')
        mock_file().write.assert_called_once_with('{"test": "json"}')
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_transcript_text(self, mock_file):
        """Test saving transcript to text file."""
        self.extractor.save_transcript_text(self.sample_transcript, "test.txt")
        
        mock_file.assert_called_once_with("test.txt", 'w', encoding='utf-8')
        expected_content = "[00:00] Hello world\n[00:02] This is a test\n[00:05] YouTube transcript"
        mock_file().write.assert_called_once_with(expected_content)
    
    @patch('transcript_extractor.extractor.requests.get')
    def test_get_video_title_success(self, mock_get):
        """Test successful video title retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {'title': 'Test Video Title'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.extractor.get_video_title("dQw4w9WgXcQ")
        
        assert result == "Test Video Title"
        expected_url = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&format=json"
        mock_get.assert_called_once_with(expected_url, timeout=10)
    
    @patch('transcript_extractor.extractor.requests.get')
    def test_get_video_title_no_title_in_response(self, mock_get):
        """Test video title retrieval when title is not in response."""
        mock_response = Mock()
        mock_response.json.return_value = {}  # No title field
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.extractor.get_video_title("dQw4w9WgXcQ")
        
        assert result == "video_dQw4w9WgXcQ"
    
    @patch('transcript_extractor.extractor.requests.get')
    def test_get_video_title_request_failure(self, mock_get):
        """Test video title retrieval when request fails."""
        mock_get.side_effect = Exception("Network error")
        
        result = self.extractor.get_video_title("dQw4w9WgXcQ")
        
        assert result == "video_dQw4w9WgXcQ"
    
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        result = self.extractor.sanitize_filename("Test Video Title")
        assert result == "Test-Video-Title"
    
    def test_sanitize_filename_with_invalid_chars(self):
        """Test filename sanitization with invalid characters."""
        result = self.extractor.sanitize_filename('Test<>:"/\\|?*Video')
        assert result == "TestVideo"
    
    def test_sanitize_filename_multiple_spaces(self):
        """Test filename sanitization with multiple spaces."""
        result = self.extractor.sanitize_filename("Test   Video   Title")
        assert result == "Test-Video-Title"
    
    def test_sanitize_filename_leading_trailing_dashes(self):
        """Test filename sanitization removes leading/trailing dashes."""
        result = self.extractor.sanitize_filename("---Test Video---")
        assert result == "Test-Video"
    
    def test_sanitize_filename_multiple_dashes(self):
        """Test filename sanitization consolidates multiple dashes."""
        result = self.extractor.sanitize_filename("Test-----Video")
        assert result == "Test-Video"
    
    def test_sanitize_filename_long_title(self):
        """Test filename sanitization with very long title."""
        long_title = "A" * 250 + " Very Long Title"
        result = self.extractor.sanitize_filename(long_title)
        assert len(result) <= 200
        assert not result.endswith('-')
    
    def test_sanitize_filename_empty_result(self):
        """Test filename sanitization when result would be empty."""
        result = self.extractor.sanitize_filename("---<>:\"/\\|?*---")
        assert result == "untitled"
    
    def test_extract_from_url_integration(self):
        """Test the extract_from_url method integration."""
        with patch.object(self.extractor, 'extract_video_id') as mock_extract_id, \
             patch.object(self.extractor, 'get_transcript') as mock_get_transcript:
            
            mock_extract_id.return_value = "dQw4w9WgXcQ"
            mock_get_transcript.return_value = self.sample_transcript
            
            result = self.extractor.extract_from_url("https://youtu.be/dQw4w9WgXcQ", "en")
            
            assert result == self.sample_transcript
            mock_extract_id.assert_called_once_with("https://youtu.be/dQw4w9WgXcQ")
            mock_get_transcript.assert_called_once_with("dQw4w9WgXcQ", "en") 