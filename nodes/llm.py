import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

_provider = os.getenv('LLM_PROVIDER', 'anthropic').lower()

if _provider == 'openai':
    from langchain_openai import ChatOpenAI
    llm_opus   = ChatOpenAI(model='gpt-4o',      temperature=0)
    llm_sonnet = ChatOpenAI(model='gpt-4o-mini', temperature=0)
    llm_haiku  = ChatOpenAI(model='gpt-4o-mini', temperature=0)

elif _provider == 'ollama':
    # Ollama exposes an OpenAI-compatible API, so we reuse the OpenAI client.
    # Works for both local Ollama and Ollama Cloud — only the endpoint/key differ:
    #   Local:  OLLAMA_BASE_URL=http://localhost:11434/v1   OLLAMA_API_KEY=ollama
    #   Cloud:  OLLAMA_BASE_URL=https://ollama.com/v1        OLLAMA_API_KEY=<your key>
    # All three tiers share one model by default; override per-tier if desired.
    from langchain_openai import ChatOpenAI
    _base  = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
    _key   = os.getenv('OLLAMA_API_KEY', 'ollama')
    _model = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
    _common = dict(base_url=_base, api_key=_key, temperature=0)
    llm_opus   = ChatOpenAI(model=os.getenv('OLLAMA_MODEL_OPUS',   _model), **_common)
    llm_sonnet = ChatOpenAI(model=os.getenv('OLLAMA_MODEL_SONNET', _model), **_common)
    llm_haiku  = ChatOpenAI(model=os.getenv('OLLAMA_MODEL_HAIKU',  _model), **_common)

else:
    from langchain_anthropic import ChatAnthropic
    llm_opus   = ChatAnthropic(model='claude-3-opus-20240229',   temperature=0)
    llm_sonnet = ChatAnthropic(model='claude-3-sonnet-20240229', temperature=0)
    llm_haiku  = ChatAnthropic(model='claude-3-haiku-20240307',  temperature=0)
