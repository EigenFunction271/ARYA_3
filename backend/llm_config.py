import os
from enum import Enum
from langchain_community.llms import HuggingFaceHub, Cohere
from langchain_community.embeddings import HuggingFaceEmbeddings, CohereEmbeddings
from groq import Groq  # Import directly from groq package

class LLMProvider(str, Enum):
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    COHERE = "cohere"

def get_llm(provider: LLMProvider):
    if provider in [LLMProvider.MISTRAL, LLMProvider.DEEPSEEK]:
        return HuggingFaceHub(
            repo_id=f"mistralai/{provider}" if provider == LLMProvider.MISTRAL else "deepseek-ai/deepseek-llm-7b-chat",
            huggingface_api_token=os.getenv("HUGGINGFACE_API_KEY")
        )
    elif provider == LLMProvider.GROQ:
        return Groq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="mixtral-8x7b-32768"
        )
    elif provider == LLMProvider.COHERE:
        return Cohere(
            api_key=os.getenv("COHERE_API_KEY"),
            model="command"
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

def get_embeddings(provider: LLMProvider):
    if provider in [LLMProvider.MISTRAL, LLMProvider.DEEPSEEK, LLMProvider.GROQ]:
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
    elif provider == LLMProvider.COHERE:
        return CohereEmbeddings(
            api_key=os.getenv("COHERE_API_KEY")
        )
    else:
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        ) 