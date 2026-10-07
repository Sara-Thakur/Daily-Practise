"""
AI-Generated Code Detection Module using Groq API ('openai/gpt-oss-120b').

Generates reference baseline solutions for DSA problems using LLM calls, then employs a
specialized 'Judge LLM' to evaluate candidate code against AI stylistic characteristics
(overly canonical structure, lack of human quirks, strict adherence to LLM formatting).
"""

from __future__ import annotations

import json
import re
from typing import List, Optional

from config import DEFAULT_MODEL, GROQ_API_KEY
from models import AIDetectionResult, Problem

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqClientWrapper:
    """
    Wrapper around the Groq Python SDK for managing model calls and prompt execution.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        """
        Initializes the Groq client.

        Args:
            api_key: Optional API key override. If omitted, uses GROQ_API_KEY from config.
            model: Groq model identifier (defaults to 'openai/gpt-oss-120b').
        """
        self.api_key = api_key or GROQ_API_KEY
        self.model = model
        self.client = None

        if Groq and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"[Warning] Failed to initialize Groq client: {e}")

    def is_available(self) -> bool:
        """Checks if Groq client is initialized and API key is present."""
        return self.client is not None

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> str:
        """
        Sends a chat completion request to the Groq API.

        Args:
            system_prompt: System role instructions.
            user_prompt: User prompt containing code or question.
            temperature: Sampling temperature for generation variability.
            max_tokens: Maximum tokens in generated response.

        Returns:
            Generated text content from model choice.
        """
        if not self.is_available():
            raise RuntimeError("Groq API client is not initialized or GROQ_API_KEY is missing.")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""


def generate_ai_baselines(
    problem: Problem,
    groq_wrapper: GroqClientWrapper,
    num_baselines: int = 3
) -> List[str]:
    """
    Generates baseline AI reference solutions for a given DSA problem prompt using Groq LLM.

    Args:
        problem: Problem object containing description and entrypoint.
        groq_wrapper: GroqClientWrapper instance.
        num_baselines: Number of independent baseline solutions to produce.

    Returns:
        List of generated Python code strings representing standard AI solutions.
    """
    if not groq_wrapper.is_available():
        # Heuristic offline baseline if Groq key is absent during local testing
        return [
            f"def {problem.entrypoint}(*args):\n    # Standard canonical AI implementation\n    pass"
        ]

    baselines: List[str] = []
    system_prompt = (
        "You are an expert Python programmer solving DSA assessment problems. "
        "Return ONLY clean, valid Python code without Markdown code block formatting or explanations."
    )

    prompt = (
        f"Problem Description:\n{problem.description}\n\n"
        f"Function Signature:\n"
        f"def {problem.entrypoint}(...):\n"
        "Provide an optimal Python implementation for this problem."
    )

    for i in range(num_baselines):
        temp = 0.2 + (i * 0.3)  # Vary temperature for solution diversity
        try:
            raw_code = groq_wrapper.generate(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=temp
            )
            cleaned_code = clean_code_block(raw_code)
            baselines.append(cleaned_code)
        except Exception as e:
            print(f"[AI Detection] Error generating baseline {i+1}: {e}")

    return baselines


def clean_code_block(text: str) -> str:
    """Strips Markdown backticks and extraneous text from LLM outputs."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def judge_ai_characteristics(
    submission_code: str,
    problem: Problem,
    baselines: List[str],
    groq_wrapper: GroqClientWrapper
) -> AIDetectionResult:
    """
    Uses a Judge LLM via Groq API ('openai/gpt-oss-120b') to evaluate AI characteristics in candidate code.

    Evaluates:
    - Overly perfect formatting and canonical variable naming.
    - Lack of idiosyncratic human errors or informal coding habits.
    - Strict adherence to AI code generation conventions and docstring styles.
    - Structural alignment with generated AI baselines.

    Args:
        submission_code: Candidate source code.
        problem: Problem object.
        baselines: AI baseline reference implementations.
        groq_wrapper: Groq API wrapper instance.

    Returns:
        AIDetectionResult object with probability, confidence, reasons, and baseline matches.
    """
    if not groq_wrapper.is_available():
        # Fallback heuristic judge if Groq is unavailable
        return AIDetectionResult(
            candidate_id="unknown",
            problem_id=problem.problem_id,
            probability=0.20,
            confidence=0.50,
            reasons=["Offline heuristic mode: Groq API key unavailable"],
            baseline_matches=[]
        )

    system_prompt = (
        "You are a Senior AI Code Forensic Auditor evaluating whether a student's submission "
        "was generated by an AI language model (e.g., ChatGPT, Claude, Copilot).\n"
        "You must analyze observable code characteristics, formatting, variable naming, "
        "comments, and structural overlap with AI baseline solutions.\n"
        "Respond ONLY in valid JSON format matching the schema requested."
    )

    baselines_text = "\n---\n".join(
        f"Baseline #{i+1}:\n{b}" for i, b in enumerate(baselines)
    )

    user_prompt = f"""
DSA Problem: {problem.title}
Problem Description: {problem.description}

Candidate Code Submission:
```python
{submission_code}
```

Generated AI Reference Baselines for Comparison:
{baselines_text}

Evaluate if the candidate's submission exhibits strong AI-generated code characteristics:
1. Overly canonical or textbook solution structure matching LLM default coding styles.
2. Lack of idiosyncratic human quirks (e.g. unique variable names, minor formatting flaws, scratch comments).
3. Highly descriptive standard type-hints and Google/Sphinx style docstrings typical of LLMs.
4. Near-identical structural overlap with the AI baselines.

Return ONLY a JSON object with this exact schema:
{{
  "probability": <float 0.0 to 1.0>,
  "confidence": <float 0.0 to 1.0>,
  "reasons": [<string list of specific observations>],
  "baseline_matches": [<string list of structural similarities with baselines>]
}}
"""

    try:
        raw_response = groq_wrapper.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0
        )
        cleaned_json = clean_code_block(raw_response)
        data = json.loads(cleaned_json)

        prob = max(0.0, min(1.0, float(data.get("probability", 0.0))))
        conf = max(0.0, min(1.0, float(data.get("confidence", 0.0))))
        reasons = data.get("reasons", [])
        matches = data.get("baseline_matches", [])

        return AIDetectionResult(
            candidate_id="candidate",
            problem_id=problem.problem_id,
            probability=round(prob, 4),
            confidence=round(conf, 4),
            reasons=reasons,
            baseline_matches=matches
        )
    except Exception as e:
        # Graceful fallback on JSON parse failure or API error
        return AIDetectionResult(
            candidate_id="candidate",
            problem_id=problem.problem_id,
            probability=0.30,
            confidence=0.40,
            reasons=[f"Judge LLM evaluation error: {str(e)}"],
            baseline_matches=[]
        )
