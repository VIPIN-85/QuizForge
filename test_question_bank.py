from pathlib import Path
import ast
import re

APP = Path(__file__).resolve().parents[1] / "app.py"

def test_app_has_question_bank_and_topics():
    source = APP.read_text(encoding="utf-8")
    assert 'TOPICS:' in source
    assert 'BANK:' in source
    assert 'def generate_questions' in source

def test_app_parses_as_python():
    ast.parse(APP.read_text(encoding="utf-8"))

def test_signature_footer_is_present():
    source = APP.read_text(encoding="utf-8")
    assert "Made with love" in source
    assert "VIPIN" in source
