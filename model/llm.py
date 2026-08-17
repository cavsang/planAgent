
from typing import Optional

from langchain.chat_models import BaseChatModel
from langchain_ollama import ChatOllama


def get_llm() ->  Optional[BaseChatModel]:
    """
    Ollama 기반의 Chat 모델 인스턴스를 반환합니다.
    Returns:
        BaseChatModel: Ollama 기반의 Chat 모델 인스턴스
    """
    return ChatOllama(
        model="Qwen3:14b",
        #model="Gemma4:26b",
        base_url="http://localhost:11434",
        temperature=0.5,
    )
    return None