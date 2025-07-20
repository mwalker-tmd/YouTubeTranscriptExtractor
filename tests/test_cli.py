"""Tests for the CLI module."""

import pytest
import argparse
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
from io import StringIO

from transcript_extractor.cli import main


class TestCLI:
    """Test cases for CLI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_transcript = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.5},
            {'text': 'This is a test', 'start': 2.5, 'duration': 3.0},
            {'text': 'YouTube transcript', 'start': 5.5, 'duration': 2.0}
        ]
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ'])
    def test_basic_extraction(self, mock_extractor_class):
        """Test basic transcript extraction."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = self.sample_transcript
        
        with patch('transcript_extractor.cli.Path.mkdir'):
            main()
            
            mock_extractor.extract_video_id.assert_called_once_with('https://youtu.be/dQw4w9WgXcQ')
            mock_extractor.get_transcript.assert_called_once_with("dQw4w9WgXcQ", None)
            mock_extractor.save_transcript_text.assert_called_once()
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--format', 'json'])
    def test_json_format(self, mock_extractor_class):
        """Test JSON format output."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = self.sample_transcript
        
        with patch('transcript_extractor.cli.Path.mkdir'):
            main()
            
            mock_extractor.save_transcript_json.assert_called_once()
            # Check that the filename ends with .json
            call_args = mock_extractor.save_transcript_json.call_args[0]
            assert call_args[1].endswith('.json')
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--language', 'es'])
    def test_language_option(self, mock_extractor_class):
        """Test language option."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = self.sample_transcript
        
        with patch('transcript_extractor.cli.Path.mkdir'), \
             patch('transcript_extractor.cli.YouTubeTranscriptExtractor.save_transcript_text'):
            
            main()
            
            mock_extractor.get_transcript.assert_called_once_with("dQw4w9WgXcQ", "es")
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--list-languages'])
    def test_list_languages(self, mock_extractor_class):
        """Test listing available languages."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_available_languages.return_value = [
            {'language': 'English', 'language_code': 'en', 'is_generated': False},
            {'language': 'Spanish', 'language_code': 'es', 'is_generated': True}
        ]
        
        with patch('builtins.print') as mock_print:
            main()
            
            mock_extractor.get_available_languages.assert_called_once_with("dQw4w9WgXcQ")
            # Check that languages were printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('English (en) (Manual)' in call for call in print_calls)
            assert any('Spanish (es) (Auto-generated)' in call for call in print_calls)
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--output', 'custom.txt'])
    def test_custom_output_filename(self, mock_extractor_class):
        """Test custom output filename."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = self.sample_transcript
        
        with patch('transcript_extractor.cli.Path.mkdir'):
            main()
            
            # Check that custom filename was used in transcripts folder
            call_args = mock_extractor.save_transcript_text.call_args[0]
            assert 'custom.txt' in str(call_args[1])
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--no-timestamps'])
    def test_no_timestamps_option(self, mock_extractor_class):
        """Test no timestamps option."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = self.sample_transcript
        
        with patch('transcript_extractor.cli.Path.mkdir'), \
             patch('builtins.open', create=True) as mock_open:
            
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            main()
            
            # Check that plain text was written (no timestamps)
            mock_file.write.assert_called_once()
            written_content = mock_file.write.call_args[0][0]
            assert '[00:00]' not in written_content
            assert 'Hello world' in written_content
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--verbose'])
    def test_verbose_output(self, mock_extractor_class):
        """Test verbose output mode."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = self.sample_transcript
        mock_extractor.format_timestamp.side_effect = lambda x: f"00:{int(x):02d}"
        
        with patch('transcript_extractor.cli.Path.mkdir'), \
             patch('transcript_extractor.cli.YouTubeTranscriptExtractor.save_transcript_text'), \
             patch('builtins.print') as mock_print:
            
            main()
            
            # Check that verbose messages were printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('Extracting video ID' in call for call in print_calls)
            assert any('Video ID: dQw4w9WgXcQ' in call for call in print_calls)
            assert any('Retrieving transcript' in call for call in print_calls)
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'invalid-url'])
    def test_invalid_url_error(self, mock_extractor_class):
        """Test error handling for invalid URL."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.side_effect = ValueError("Could not extract video ID")
        
        with patch('builtins.print') as mock_print, \
             pytest.raises(SystemExit) as exc_info:
            
            main()
            
            assert exc_info.value.code == 1
            # Check that error was printed to stderr
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('Error:' in call for call in print_calls)
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ'])
    def test_transcript_error(self, mock_extractor_class):
        """Test error handling for transcript retrieval failure."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.side_effect = Exception("Transcript not available")
        
        with patch('builtins.print') as mock_print, \
             pytest.raises(SystemExit) as exc_info:
            
            main()
            
            assert exc_info.value.code == 1
            # Check that error and possible reasons were printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('Error:' in call for call in print_calls)
            assert any('Possible reasons:' in call for call in print_calls)
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--output', '/absolute/path/file.txt'])
    def test_absolute_output_path(self, mock_extractor_class):
        """Test absolute output path handling."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = self.sample_transcript
        
        with patch('transcript_extractor.cli.Path.mkdir'):
            main()
            
            # Check that absolute path was used directly
            call_args = mock_extractor.save_transcript_text.call_args[0]
            assert '/absolute/path/file.txt' in str(call_args[1])
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ'])
    def test_transcripts_folder_creation(self, mock_extractor_class):
        """Test that transcripts folder is created."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = self.sample_transcript
        
        with patch('transcript_extractor.cli.Path.mkdir') as mock_mkdir, \
             patch('transcript_extractor.cli.YouTubeTranscriptExtractor.save_transcript_text'):
            
            main()
            
            # Check that transcripts directory was created
            mock_mkdir.assert_called_once_with(exist_ok=True)
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ'])
    def test_title_fetch_fallback(self, mock_extractor_class):
        """Test fallback when title fetch fails."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.side_effect = Exception("Network error")
        mock_extractor.get_transcript.return_value = self.sample_transcript
        
        with patch('transcript_extractor.cli.Path.mkdir'):
            main()
            
            # Should still work and use video ID as fallback
            mock_extractor.save_transcript_text.assert_called_once()
            call_args = mock_extractor.save_transcript_text.call_args[0]
            assert 'video_dQw4w9WgXcQ' in str(call_args[1]) 