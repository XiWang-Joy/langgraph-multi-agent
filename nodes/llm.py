import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

_provider = os.getenv('LLM_PROVIDER', 'anthropic').lower()

if _provider == 'openai':
    from langchain_openai import ChatOpenAI
    llm_opus   = ChatOpenAI(model='gpt-4o',      temperature=0)
    llm_sonnet = ChatOpenAI(model='gpt-4o-mini', temperature=0)
    llm_haiku  = ChatOpenAI(model='gpt-4o-mini', temperature=0)
else:
    from langchain_anthropic import ChatAnthropic
    llm_opus   = ChatAnthropic(model='claude-3-opus-20240229',   temperature=0)
    llm_sonnet = ChatAnthropic(model='claude-3-sonnet-20240229', temperature=0)
    llm_haiku  = ChatAnthropic(model='claude-3-haiku-20240307',  temperature=0)
