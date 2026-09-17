
from typing import Optional

from langchain.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv

load_dotenv()

def get_llm() ->  Optional[BaseChatModel]:
    """
    Ollama 기반의 Chat 모델 인스턴스를 반환합니다.
    Returns:
        BaseChatModel: Ollama 기반의 Chat 모델 인스턴스
    """
    #model="Gemma4:26b"
    #return ChatOllama(model="Qwen3:14b",base_url="http://localhost:11434",temperature=0.4, top_p=0.8,think=True, verbose=True)
    return ChatOpenAI(model="gpt-5-mini", temperature=0)


def get_Blueprint(type:str) -> Optional[BaseChatModel]:
    if type == "수학" or type == "과학":
        return get_llm_o4_mini("medium")
    else:
        return get_llm_5mini(0.2)

def get_Generation(type:str) -> Optional[BaseChatModel]:
    if type == "수학" or type == "과학":
        return get_llm_5mini()
    else:
        return get_llm_5_5()

def get_verification(type:str) -> Optional[BaseChatModel]:
    if type == "수학" or type == "과학":
        return get_llm_o4_mini()
    else:
        return get_llm_5_5(0.1)





def get_llm_o4_mini(reasoning_effort = None) -> Optional[BaseChatModel]:
    """수학/과학에 좋다함."""
    if reasoning_effort:
        return ChatOpenAI(model="o4-mini", reasoning_effort=reasoning_effort)
    else:
        return ChatOpenAI(model="o4-mini") #o4-mini 는 temperature를 지원하지않는다.기본적으로 1

def get_llm_5mini(temp = 0.1) -> Optional[BaseChatModel]:
    """Route등 기본적인거에 좋다함."""
    return ChatOpenAI(model="gpt-5-mini", temperature=temp)

def get_llm_5_5(temp = 0.3) -> Optional[BaseChatModel]:
    """긴문장/국어/사회/영어에 좋음"""
    return ChatOpenAI(model="gpt-5.5", temperature=temp)


