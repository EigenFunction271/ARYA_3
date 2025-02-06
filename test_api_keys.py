import os
from dotenv import load_dotenv
from backend.llm_config import get_llm, LLMProvider


load_dotenv()

def test_key(provider: str, env_var: str):
    key = os.getenv(env_var)
    print(f"\n{provider} API Key:")
    print(f"- Present: {bool(key)}")
    print(f"- Length: {len(key) if key else 0}")
    print(f"- Format: {'Valid' if key and len(key) > 20 else 'Invalid'}")

# Test each provider
test_key("HuggingFace", "HUGGINGFACE_API_KEY")
test_key("Groq", "GROQ_API_KEY")
test_key("Cohere", "COHERE_API_KEY")