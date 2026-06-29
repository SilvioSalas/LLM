#=========================================================
# Configuração do ambiente
#=========================================================

import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)
#=========================================================
# Prompt do sistema
#=========================================================
SYSTEM_PROMPT = """
Você é um especialista em Engenharia de Prompt.

Ajude o usuário a construir prompts de alta qualidade.

Sempre:

- responda em português;
- seja técnico;
- utilize exemplos;
- explique o raciocínio quando solicitado.
"""
#=========================================================
# Inicialização do histórico
#=========================================================
if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role":"system",
            "content":SYSTEM_PROMPT
        },

        {
            "role":"assistant",
            "content":"Olá! Como posso ajudar?"
        }

    ]

#=========================================================
# Mostrar histórico
#=========================================================
for msg in st.session_state.messages:

    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

#=========================================================
# Entrada do usuário
#=========================================================
question = st.chat_input("Digite sua pergunta...")

#=========================================================
# Adiciona ao histórico
#=====================================================
if question:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)
#=========================================================
# Streaming
#=========================================================
# A API da NVIDIA devolve pequenos pedaços (delta.content).
with st.chat_message("assistant"):

    placeholder = st.empty()

    answer = ""

    stream = client.chat.completions.create(

        model="deepseek-ai/deepseek-v4-flash",

        messages=st.session_state.messages,

        temperature=1,

        top_p=0.95,

        max_tokens=16384,

        stream=True,

        extra_body={
            "chat_template_kwargs":{
                "thinking":True,
                "reasoning_effort":"high"
            }
        }

    )

    for chunk in stream:

        delta = chunk.choices[0].delta

        if delta.content:

            answer += delta.content

            placeholder.markdown(answer + "▌")

    placeholder.markdown(answer)

#=====================================================
# Salva no histórico
#========================== 
st.session_state.messages.append(

    {
        "role":"assistant",
        "content":answer
    }

)

#=====================================================
# Limpar conversa
#=====================================================
if st.button("Limpar conversa"):

    st.session_state.messages=[

        {
            "role":"system",
            "content":SYSTEM_PROMPT
        },

        {
            "role":"assistant",
            "content":"Olá! Como posso ajudar?"
        }

    ]

    st.rerun()