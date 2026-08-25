
from typing import Optional

from langchain.chat_models import BaseChatModel
#from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv

load_dotenv()
# API 키 설정
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "password"


def get_llm() ->  Optional[BaseChatModel]:
    """
    Ollama 기반의 Chat 모델 인스턴스를 반환합니다.
    Returns:
        BaseChatModel: Ollama 기반의 Chat 모델 인스턴스
    """
    #model="Gemma4:26b"
    #return ChatOllama(model="Qwen3:14b",base_url="http://localhost:11434",temperature=0.5,)
    return ChatOpenAI(model="gpt-5-mini", temperature=0)
    #return None
