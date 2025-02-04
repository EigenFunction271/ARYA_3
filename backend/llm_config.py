import os
from enum import Enum
from langchain_community.llms import HuggingFaceHub, Groq, Cohere
from langchain_community.embeddings import HuggingFaceEmbeddings, CohereEmbeddings

class LLMProvider(str, Enum):
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    COHERE = "cohere"

def get_llm(provider: LLMProvider = LLMProvider.MISTRAL):
    """Get LLM based on provider"""
    if provider == LLMProvider.MISTRAL:
        return HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            model_kwargs={"temperature": 0.7, "max_length": 512}
        )
    elif provider == LLMProvider.DEEPSEEK:
        return HuggingFaceHub(
            repo_id="deepseek-ai/deepseek-coder-7b-instruct",
            model_kwargs={"temperature": 0.7, "max_length": 512}
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

def get_embeddings(provider: LLMProvider = LLMProvider.MISTRAL):
    """Get embeddings based on provider"""
    if provider in [LLMProvider.MISTRAL, LLMProvider.DEEPSEEK]:
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
    elif provider == LLMProvider.COHERE:
        return CohereEmbeddings(
            api_key=os.getenv("COHERE_API_KEY")
        )
    else:
        # Default to HuggingFace embeddings for other providers
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        ) 