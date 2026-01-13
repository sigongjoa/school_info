"""Tests for src/pdf_gen.py"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from src.pdf_gen import TypstGenerator


@pytest.fixture
def generator():
    with patch('src.pdf_gen.TypstGenerator._discover_fonts', return_value=[]):
        return TypstGenerator()


def test_generator_initialization_with_fonts():
    """Test generator initialization with found fonts"""
    with patch('src.pdf_gen.TypstGenerator._discover_fonts', return_value=["/usr/share/fonts/nanum"]):
        gen = TypstGenerator()

        assert len(gen.font_paths) == 1
        assert gen.font_arg == ["--font-path", "/usr/share/fonts/nanum"]


def test_generator_initialization_without_fonts():
    """Test generator initialization without fonts"""
    with patch('src.pdf_gen.TypstGenerator._discover_fonts', return_value=[]):
        gen = TypstGenerator()

        assert len(gen.font_paths) == 0
        assert gen.font_arg == []


def test_discover_fonts(generator):
    """Test font discovery"""
    with patch('os.path.exists') as mock_exists:
        mock_exists.side_effect = [True, False, True]  # First and third exist

        fonts = generator._discover_fonts()

        assert len(fonts) == 2
        assert "/usr/share/fonts/truetype/nanum" in fonts
        assert "/root/.local/share/fonts" in fonts


def test_compile_success(generator):
    """Test successful Typst compilation"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False) as template_file:
        template_file.write("#import \"data.json\": *\n")
        template_path = template_file.name

    output_path = template_path.replace('.typ', '.pdf')
    data = {"title": "Test", "content": "Test content"}

    try:
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            generator.compile(template_path, data, output_path)

            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "typst" in call_args
            assert "compile" in call_args
            assert template_path in call_args
            assert output_path in call_args
    finally:
        if os.path.exists(template_path):
            os.unlink(template_path)
        json_path = template_path.replace('.typ', '.json')
        if os.path.exists(json_path):
            os.unlink(json_path)


def test_compile_creates_data_file(generator):
    """Test that compile creates a JSON data file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False) as f:
        template_path = f.name

    output_path = template_path.replace('.typ', '.pdf')
    data = {"key": "value", "number": 42}

    try:
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            generator.compile(template_path, data, output_path)

            # Check that JSON file was created
            json_path = template_path.replace('.typ', '.json')
            assert os.path.exists(json_path)

            # Verify JSON content
            with open(json_path, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == data
    finally:
        for path in [template_path, output_path, template_path.replace('.typ', '.json')]:
            if os.path.exists(path):
                os.unlink(path)


def test_compile_failure(generator):
    """Test Typst compilation failure"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False) as f:
        template_path = f.name

    output_path = template_path.replace('.typ', '.pdf')

    try:
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "typst", stderr="Compilation error"
            )

            with pytest.raises(RuntimeError) as exc_info:
                generator.compile(template_path, {}, output_path)

            assert "Typst Error" in str(exc_info.value)
    finally:
        for path in [template_path, template_path.replace('.typ', '.json')]:
            if os.path.exists(path):
                os.unlink(path)


def test_compile_with_font_arg(generator):
    """Test compile includes font argument when fonts are available"""
    generator.font_arg = ["--font-path", "/test/fonts"]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.typ', delete=False) as f:
        template_path = f.name

    output_path = template_path.replace('.typ', '.pdf')

    try:
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            generator.compile(template_path, {}, output_path)

            call_args = mock_run.call_args[0][0]
            assert "--font-path" in call_args
            assert "/test/fonts" in call_args
    finally:
        for path in [template_path, template_path.replace('.typ', '.json')]:
            if os.path.exists(path):
                os.unlink(path)


# Add missing import
import subprocess
