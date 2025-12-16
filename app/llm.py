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

from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()


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
    callbacks=[langfuse_handler], 
)

# Async LLM for high-performance scenarios
async_llm = ChatOpenAI(
    # model="gpt-4o-mini",
    # temperature=0,
    # api_key=OPENAI_API_KEY,
    # max_retries=OPENAI_MAX_RETRIES,
    # timeout=OPENAI_TIMEOUT,
    # max_tokens=OPENAI_MAX_TOKENS,
    # streaming=False
    model=LLM_MODEL,
    temperature=0,
    base_url=OPENAI_URI,
    api_key=OPENAI_API_KEY,
    max_retries=OPENAI_MAX_RETRIES,
    timeout=OPENAI_TIMEOUT,
    max_tokens=OPENAI_MAX_TOKENS,
    streaming=False,
    callbacks=[langfuse_handler]
)