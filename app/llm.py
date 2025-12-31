import asyncio
from langchain_openai import ChatOpenAI

from .config import (
    OPENAI_API_KEY, 
    OPENAI_URI,
    OPENAI_MAX_RETRIES, 
    OPENAI_TIMEOUT,
    OPENAI_MAX_TOKENS,
    LLM_MODEL,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_HOST
)

# Try to import Langfuse callback handler
try:
    from langfuse.callback import CallbackHandler
    langfuse_handler = CallbackHandler(
        secret_key=LANGFUSE_SECRET_KEY,
        public_key=LANGFUSE_PUBLIC_KEY,
        host=LANGFUSE_HOST
    ) if LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY else None
except ImportError:
    print("Warning: Langfuse not available. Continuing without tracing.")
    langfuse_handler = None

# Prepare callbacks
callbacks = [langfuse_handler] if langfuse_handler else []

# Synchronous LLM for current workflow
llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=0,
    base_url=OPENAI_URI,
    api_key=OPENAI_API_KEY,
    max_retries=OPENAI_MAX_RETRIES,
    timeout=OPENAI_TIMEOUT,
    max_tokens=OPENAI_MAX_TOKENS,
    streaming=False,
    callbacks=callbacks, 
)

# Async LLM for high-performance scenarios
async_llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=0,
    base_url=OPENAI_URI,
    api_key=OPENAI_API_KEY,
    max_retries=OPENAI_MAX_RETRIES,
    timeout=OPENAI_TIMEOUT,
    max_tokens=OPENAI_MAX_TOKENS,
    streaming=False,
    callbacks=callbacks
)