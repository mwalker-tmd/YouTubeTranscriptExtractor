"""Tests for file conflict handling functionality."""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import tempfile
import os

from transcript_extractor.cli import handle_file_conflict, get_unique_filename, main


class TestFileConflictHandling:
    """Test cases for file conflict handling."""
    
    def test_handle_file_conflict_no_conflict(self):
        """Test conflict handling when file doesn't exist."""
        non_existent_path = Path("non_existent_file.txt")
        
        result = handle_file_conflict(non_existent_path, "prompt")
        
        assert result == non_existent_path
    
    def test_handle_file_conflict_replace_mode(self):
        """Test conflict handling in replace mode."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = Path(tmp.name)
            
        try:
            result = handle_file_conflict(file_path, "replace")
            assert result == file_path
        finally:
            if file_path.exists():
                file_path.unlink()
    
    def test_handle_file_conflict_abort_mode(self):
        """Test conflict handling in abort mode."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = Path(tmp.name)
            
        try:
            result = handle_file_conflict(file_path, "abort")
            assert result is None
        finally:
            if file_path.exists():
                file_path.unlink()
    
    def test_handle_file_conflict_rename_mode(self):
        """Test conflict handling in rename mode."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            file_path = Path(tmp.name)
            
        try:
            result = handle_file_conflict(file_path, "rename")
            
            assert result != file_path
            assert result.suffix == file_path.suffix
            assert f"{file_path.stem}(1)" in str(result)
            assert not result.exists()
        finally:
            if file_path.exists():
                file_path.unlink()
    
    @patch('builtins.input', side_effect=['R'])
    def test_handle_file_conflict_prompt_replace(self, mock_input):
        """Test conflict handling with prompt choosing replace."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = Path(tmp.name)
            
        try:
            with patch('builtins.print'):
                result = handle_file_conflict(file_path, "prompt")
            
            assert result == file_path
            mock_input.assert_called_once()
        finally:
            if file_path.exists():
                file_path.unlink()
    
    @patch('builtins.input', side_effect=['C'])
    def test_handle_file_conflict_prompt_create(self, mock_input):
        """Test conflict handling with prompt choosing create new."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            file_path = Path(tmp.name)
            
        try:
            with patch('builtins.print'):
                result = handle_file_conflict(file_path, "prompt")
            
            assert result != file_path
            assert f"{file_path.stem}(1)" in str(result)
            mock_input.assert_called_once()
        finally:
            if file_path.exists():
                file_path.unlink()
    
    @patch('builtins.input', side_effect=['A'])
    def test_handle_file_conflict_prompt_abort(self, mock_input):
        """Test conflict handling with prompt choosing abort."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = Path(tmp.name)
            
        try:
            with patch('builtins.print'):
                result = handle_file_conflict(file_path, "prompt")
            
            assert result is None
            mock_input.assert_called_once()
        finally:
            if file_path.exists():
                file_path.unlink()
    
    @patch('builtins.input', side_effect=['X', 'invalid', 'R'])
    def test_handle_file_conflict_prompt_invalid_then_valid(self, mock_input):
        """Test conflict handling with invalid inputs then valid choice."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = Path(tmp.name)
            
        try:
            with patch('builtins.print'):
                result = handle_file_conflict(file_path, "prompt")
            
            assert result == file_path
            assert mock_input.call_count == 3
        finally:
            if file_path.exists():
                file_path.unlink()
    
    def test_get_unique_filename_basic(self):
        """Test unique filename generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "test.txt"
            
            # Create the base file
            base_path.touch()
            
            result = get_unique_filename(base_path)
            
            expected = Path(tmpdir) / "test(1).txt"
            assert result == expected
            assert not result.exists()
    
    def test_get_unique_filename_multiple_conflicts(self):
        """Test unique filename generation with multiple existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "test.txt"
            conflict1 = Path(tmpdir) / "test(1).txt"
            conflict2 = Path(tmpdir) / "test(2).txt"
            
            # Create conflicting files
            base_path.touch()
            conflict1.touch()
            conflict2.touch()
            
            result = get_unique_filename(base_path)
            
            expected = Path(tmpdir) / "test(3).txt"
            assert result == expected
            assert not result.exists()
    
    def test_get_unique_filename_no_extension(self):
        """Test unique filename generation for files without extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "test"
            
            base_path.touch()
            
            result = get_unique_filename(base_path)
            
            expected = Path(tmpdir) / "test(1)"
            assert result == expected
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--conflict', 'replace'])
    def test_cli_conflict_replace(self, mock_extractor_class):
        """Test CLI with conflict replace mode."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = [
            {'text': 'Hello', 'start': 0.0, 'duration': 1.0}
        ]
        
        with patch('transcript_extractor.cli.Path.mkdir'), \
             patch('transcript_extractor.cli.handle_file_conflict') as mock_conflict:
            
            mock_conflict.return_value = Path("transcripts/Test-Video.txt")
            
            main()
            
            mock_conflict.assert_called_once()
            call_args = mock_conflict.call_args[0]
            assert call_args[1] == "replace"
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--conflict', 'abort'])
    def test_cli_conflict_abort(self, mock_extractor_class):
        """Test CLI with conflict abort mode that actually aborts."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = [
            {'text': 'Hello', 'start': 0.0, 'duration': 1.0}
        ]
        
        with patch('transcript_extractor.cli.Path.mkdir'), \
             patch('transcript_extractor.cli.handle_file_conflict') as mock_conflict, \
             patch('builtins.print') as mock_print:
            
            mock_conflict.return_value = None  # Simulate abort
            
            main()
            
            # Should print abort message and not call save methods
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('Operation aborted' in call for call in print_calls)
            mock_extractor.save_transcript_text.assert_not_called()
    
    @patch('transcript_extractor.cli.YouTubeTranscriptExtractor')
    @patch('sys.argv', ['transcript-extractor', 'https://youtu.be/dQw4w9WgXcQ', '--conflict', 'rename', '--verbose'])
    def test_cli_conflict_rename_verbose(self, mock_extractor_class):
        """Test CLI with conflict rename mode and verbose output."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.extract_video_id.return_value = "dQw4w9WgXcQ"
        mock_extractor.get_video_title.return_value = "Test Video"
        mock_extractor.sanitize_filename.return_value = "Test-Video"
        mock_extractor.get_transcript.return_value = [
            {'text': 'Hello', 'start': 0.0, 'duration': 1.0}
        ]
        
        with patch('transcript_extractor.cli.Path.mkdir'), \
             patch('transcript_extractor.cli.handle_file_conflict') as mock_conflict, \
             patch('builtins.print') as mock_print:
            
            # Simulate renamed file
            intended = Path("transcripts/Test-Video.txt")
            renamed = Path("transcripts/Test-Video(1).txt")
            mock_conflict.return_value = renamed
            
            main()
            
            # Should print message about using renamed filename
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('Using filename:' in call and 'Test-Video(1).txt' in call for call in print_calls) 