import os
from typing import Type, TypeVar

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


load_dotenv()

T = TypeVar("T", bound=BaseModel)


class ResumeData(BaseModel):
    name: str = ""
    skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    years_experience: float = 0.0
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class JobRequirements(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_required: str = ""
    required_experience_years: float = 0.0
    education_required: list[str] = Field(default_factory=list)


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def extract_structured_data(
    prompt: str,
    response_schema: Type[T]
) -> T:
    """
    Extract structured Pydantic data using Gemini.

    Uses the current Gemini model configured for the project.
    """

    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.0,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response_schema.model_validate_json(response.text)

    except Exception as exc:
        raise RuntimeError(
            f"Gemini API Extraction failed: {exc}"
        ) from exc