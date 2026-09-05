import os
from typing import Type, TypeVar

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

T = TypeVar("T", bound=BaseModel)

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


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

    tools: list[str] = Field(default_factory=list)

    technologies: list[str] = Field(default_factory=list)

    responsibilities: list[str] = Field(default_factory=list)

    tools: list[str] = Field(default_factory=list)

    technologies: list[str] = Field(
        default_factory=list
    )

    responsibilities: list[str] = Field(
        default_factory=list
    )


def get_gemini_client() -> genai.Client:
    """
    Create Gemini client using API key
    stored in environment variables.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Create a .env file and add:"
            "\nGEMINI_API_KEY=your_key"
        )

    return genai.Client(api_key=api_key)


def extract_structured_data(
    prompt: str,
    response_schema: Type[T]
) -> T:
    """
    Extract structured JSON from Gemini
    and validate it using Pydantic.
    """

    client = get_gemini_client()

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.0,
            ),
        )

        if response is None:
            raise RuntimeError(
                "Gemini returned no response."
            )

        if not response.text:
            raise RuntimeError(
                "Gemini returned empty text."
            )

        return response_schema.model_validate_json(
            response.text
        )

    except ValidationError as e:
        raise RuntimeError(
            f"Invalid JSON schema returned "
            f"by Gemini:\n{e}"
        )

    except ValueError:
        raise

    except Exception as e:
        raise RuntimeError(
            f"Gemini extraction failed: {e}"
        ) from e
