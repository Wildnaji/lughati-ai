"""
AI model and prompt logic for Lughati AI.
Handles mode-to-prompt mapping and OpenAI API calls.
"""
from typing import Dict, Optional
import openai
from back_end.config import get_openai_api_key, get_openai_model, get_api_timeout


# System prompts for each mode
MODE_PROMPTS: Dict[str, str] = {
    "grammar_fix": (
        "You are an expert Arabic language editor. "
        "Correct grammar, spelling, and sentence structure in Modern Standard Arabic. "
        "Preserve the original meaning. Do not explain; return only the corrected text."
    ),
    "professional_arabic": (
        "You are a professional Arabic writer. "
        "Rewrite the text in clear, concise, and formal Modern Standard Arabic "
        "suitable for business, government, and corporate communication in the GCC. "
        "Keep the same meaning."
    ),
    "emirati_dialect": (
        "You are an expert in Emirati Arabic. "
        "Rewrite the text in fluent Emirati dialect, natural for UAE locals. "
        "Avoid Egyptian or Levantine phrasing. Keep the original meaning."
    ),
    "academic_tone": (
        "You are an academic Arabic writer. "
        "Rewrite the text in a formal, academic tone, suitable for research assignments "
        "or university work. Keep the original meaning but improve clarity and structure."
    ),
    "marketing_tone": (
        "You are a creative Arabic copywriter. "
        "Rewrite the text in engaging, persuasive marketing Arabic suitable for "
        "social media or ads in the GCC. Preserve the core message but make it attractive and catchy."
    ),
    "translate_en_ar": (
        "You are a professional translator. "
        "Translate from English to Arabic, targeting GCC readers. "
        "Use neutral, clear language unless the source text uses slang or a casual tone."
    ),
    "translate_ar_en": (
        "You are a professional translator. "
        "Translate from Arabic to English in a clear, professional tone. "
        "Preserve the meaning, avoid literal word-for-word translation if it harms clarity."
    ),
}


def get_system_prompt(mode: str) -> str:
    """
    Get the system prompt for a given mode.
    
    Args:
        mode: The mode identifier (e.g., "grammar_fix", "professional_arabic")
    
    Returns:
        The system prompt string for that mode
    
    Raises:
        ValueError: If the mode is not recognized
    """
    if mode not in MODE_PROMPTS:
        raise ValueError(
            f"Unknown mode: {mode}. "
            f"Available modes: {', '.join(MODE_PROMPTS.keys())}"
        )
    return MODE_PROMPTS[mode]


def generate_text(text: str, mode: str, api_key: Optional[str] = None) -> str:
    """
    Generate corrected/rewritten/translated text using OpenAI API.
    
    Args:
        text: The input text to process
        mode: The processing mode (e.g., "grammar_fix", "professional_arabic")
        api_key: Optional OpenAI API key. If not provided, uses server env var.
    
    Returns:
        The generated text result
    
    Raises:
        ValueError: If mode is invalid
        Exception: If OpenAI API call fails
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")
    
    system_prompt = get_system_prompt(mode)
    model = get_openai_model()
    
    # Use provided API key or fall back to environment variable
    # SECURITY: Never log or expose API keys
    if api_key:
        openai_key = api_key
    else:
        try:
            openai_key = get_openai_api_key()
        except ValueError:
            raise Exception("OpenAI API key is required. Please provide one in the X-OPENAI-KEY header or set OPENAI_API_KEY environment variable.")
    
    try:
        # SECURITY: API key is passed directly to OpenAI client, never logged
        client = openai.OpenAI(api_key=openai_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            timeout=get_api_timeout()
        )
        
        result = response.choices[0].message.content.strip()
        return result
    
    except openai.OpenAIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating text: {str(e)}")


