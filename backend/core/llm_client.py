# backend/core/llm_client.py
import os
from backend.config import Config
from backend.core.logger import get_logger

from langchain.chat_models import AzureChatOpenAI
from langchain_openai import ChatOpenAI  # standard OpenAI
from langchain_groq import ChatGroq      # Groq client (if installed)

logger = get_logger(__name__)

def get_llm(model_type: str = "azure"):
    """
    Factory to return an LLM client instance.
    Supports Azure OpenAI, OpenAI, and Groq.
    """
    model_type = model_type.lower()

    if model_type == "azure":
        logger.info("🔹 Using Azure OpenAI LLM")
        return AzureChatOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_deployment=Config.AZURE_OPENAI_DEPLOYMENT,
            temperature=0.3
        )

    elif model_type == "openai":
        logger.info("🔹 Using OpenAI LLM")
        return ChatOpenAI(model=Config.OPENAI_MODEL, api_key=Config.OPENAI_API_KEY)

    elif model_type == "groq":
        logger.info("🔹 Using Groq LLM")
        return ChatGroq(model=Config.GROQ_MODEL, api_key=Config.GROQ_API_KEY)

    else:
        raise ValueError(f"Unsupported LLM provider: {model_type}")
