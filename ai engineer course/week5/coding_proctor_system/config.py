"""
Configuration module for the Automated Coding Multiagent Proctoring System.

Handles environment variables, Groq API settings, detection thresholds,
and file path definitions for the online coding assessment system.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current directory, parent directories, or workspace root
env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Risk Assessment Thresholds & Weights
RISK_THRESHOLD = 0.70  # Submissions with risk score > 0.70 are flagged for investigation
SIMILARITY_WEIGHT = 0.35  # Weight for MOSS structural code similarity
BUG_SIMILARITY_WEIGHT = 0.35  # Weight for identical failure patterns on hidden test cases
AI_DETECTION_WEIGHT = 0.30  # Weight for LLM Judge AI-generated code detection

# Directory Layout for Assessment Engine
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROBLEMS_DIR = DATA_DIR / "problems"
SUBMISSIONS_DIR = DATA_DIR / "submissions"
AI_REFERENCES_DIR = DATA_DIR / "ai_references"
REPORTS_DIR = DATA_DIR / "reports"

# MOSS Winnowing Parameters
MOSS_KGRAM_SIZE = 6  # Length of token n-grams
MOSS_WINDOW_SIZE = 4  # Winnowing window size for fingerprint selection
