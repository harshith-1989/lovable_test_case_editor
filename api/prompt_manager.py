"""
Prompt management and Gemini AI integration utilities
(using the official google-genai Python SDK with structured output schema).

Handles:
- Structured prompt generation (JSON-LD / OpenAPI schema)
- Secure Gemini execution with schema validation
- Robust JSON extraction and sanitization
"""

import os
import json
from utils.logger import get_logger
from typing import Dict, Any, Optional

from google import genai
from google.genai.types import Schema, GenerateContentConfig

logger = get_logger(__name__)


# ------------------------------------------------------------------------------
# 🎯 PromptManager — Strict JSON-LD / OpenAPI-Compatible Output
# ------------------------------------------------------------------------------

class PromptManager:
    """
    Crafts a structured prompt ensuring Gemini produces strict JSON-LD
    compliant with OpenAPI-like schema for vulnerability metadata.
    """

    CONTEXT_URL = "https://schema.org/SecurityVulnerability"

    JSON_SCHEMA = {
        "@context": "https://schema.org/",
        "@type": "SecurityVulnerability",
        "owasp_ref": "string",
        "compliance": "string",
        "vuln_abstract": "string",
        "description": "string",
        "recommendation": "string",
        "example": "string"
    }

    def build_prompt(self, vuln_name: str, platform: str) -> str:
        """
        Builds a contextually rich prompt for Gemini structured output.
        """
        return f"""
You are a senior cybersecurity analyst and GenAI engineer.

Given the vulnerability/test-case name "{vuln_name}" and platform "{platform}",
generate a concise, accurate, and structured JSON-LD object describing
the vulnerability and its associated metadata.

Follow OWASP standards, NIST AI RMF, and ISO/IEC 5338:2023 when applicable.

Each field must:
- Be factual and relevant to the specified platform.
- Avoid generic definitions.
- Return only one JSON object (no markdown, no explanations).
        """.strip()


# ------------------------------------------------------------------------------
# 🤖 GeminiClient — Executes prompt using Google GenAI SDK (Structured Output)
# ------------------------------------------------------------------------------

class GeminiClient:
    """
    Wrapper for Google Gemini (gemini-2.5-flash or later)
    using structured output schema enforcement.
    """

    MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    TIMEOUT = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "20"))

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing environment variable: GEMINI_API_KEY")

        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            logger.exception("Failed to initialize Google GenAI client.")
            raise RuntimeError("Gemini client initialization failed") from e

        logger.info(f"Initialized Google GenAI client with model: {self.MODEL}")

        # Prebuild structured schema
        self.response_schema = Schema(
            type="object",
            properties={
                "@context": Schema(type="string", default="https://schema.org/"),
                "@type": Schema(type="string", default="SecurityVulnerability"),
                "owasp_ref": Schema(type="string", description="Platform-specific OWASP mapping(only one from the latest OWASP for the platforms: 1)Web/API/LLM in the format OWASP top 10 <year>:<Ax for web/API or LLMx for LLM> - <top-10 name>). 2)Mobile in the format MASVS-<category>-<x>"),
                "compliance": Schema(type="string", description="Applicable compliance frameworks like NIST, ISO."),
                "vuln_abstract": Schema(type="string",
                                        description="Brief summary of the vulnerability and its potential impact."),
                "description": Schema(type="string", description="Detailed description of the vulnerability."),
                "recommendation": Schema(type="string", description="Mitigation and remediation recommendations."),
                "example": Schema(type="string", description="Example exploit scenario for this vulnerability.")
            },
            required=[
                "owasp_ref", "compliance", "vuln_abstract",
                "description", "recommendation", "example"
            ]
        )

    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generates structured JSON output from Gemini.
        """
        try:
            config = GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=self.response_schema,
                max_output_tokens=2000
            )

            logger.info("Invoking Gemini with structured schema enforcement...")
            response = self.client.models.generate_content(
                model=self.MODEL,
                contents=prompt,
                config=config
            )
            logger.info(f"gemeni output: {response}")
            if hasattr(response, "parsed") and response.parsed:
                logger.info("Gemini returned structured parsed output.")
                return response.parsed  # Already a dict (schema-enforced)

            # fallback — manually parse if SDK changes format
            if hasattr(response, "text"):
                text = response.text.strip()
                return json.loads(text)

            return {}

        except Exception as e:
            logger.exception("Gemini structured generation failed.")
            raise RuntimeError(f"Gemini structured generation failed: {e}") from e


# ------------------------------------------------------------------------------
# 🧩 Helper — Robust JSON Extractor (fallback for manual parsing)
# ------------------------------------------------------------------------------

def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to extract JSON from non-schema model outputs.
    Useful for fallback paths or testing older models.
    """
    if not text:
        return None
    try:
        return json.loads(str(text))
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except Exception:
                sanitized = candidate.replace("'", "\"")
                try:
                    return json.loads(sanitized)
                except Exception:
                    return None
    return None
