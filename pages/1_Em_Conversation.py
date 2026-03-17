import streamlit as st
from Home import setup
from pathlib import Path
from utils.mongodb import log_transcript
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI


if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

MAXIMUM_RESPONSES = 1000

client = setup()

st.title("Chat with Em (Week 4)")

# Load data only once
persist_dir = Path(__file__).resolve().parent.parent / "storage"
@st.cache_resource
def load_index():
    storage_context = StorageContext.from_defaults(
        persist_dir=str(persist_dir),
    )
    return load_index_from_storage(storage_context)

llm = OpenAI(model=st.session_state["model"])
index = load_index()
chat_engine = index.as_chat_engine(llm=llm)

# Bot initiates the conversation
if not st.session_state.chat_history:
    
    with st.chat_message("assistant", avatar="images/Em Icon.png"):
        initial_prompt = st.session_state["em_prompt"]

        response = chat_engine.chat(initial_prompt)

        message = {"content": str(response), "role": "assistant"}
        st.session_state.chat_history.append(message)
        st.markdown(message["content"])


else:
    # Write chat history
    for message in st.session_state.chat_history:

        if message["role"]=='assistant': avatar="images/Em Icon.png"
        else: avatar=None

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Chat logic
if prompt := st.chat_input(
    "Write a response here",
    disabled=st.session_state.em_conversation_finished or st.session_state.response_counter >= MAXIMUM_RESPONSES
):

    st.session_state.chat_history.append({"role": "user", "content": prompt})

    if st.session_state.response_counter < MAXIMUM_RESPONSES:
    
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="images/Em Icon.png"):
            # LlamaIndex requires chat_history to use ChatMessage objects, Streamlit requires dicts. 
            # Necessary to translate between the two formats.
            messages_with_system_prompt = [ChatMessage(role=MessageRole.SYSTEM, content=str(st.session_state["em_prompt"]))] + [
                ChatMessage(role=m["role"], content=m["content"])
            for m in st.session_state.chat_history
            ]

            response = chat_engine.chat(prompt,chat_history=messages_with_system_prompt)
            st.markdown(response)
            
        st.session_state.response_counter += 1
        st.session_state.chat_history.append({"role": "assistant", "content": str(response)})

    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message = "Well done, I hope I was of assistance."
            st.markdown(message)
        
        final_message = {"role": "assistant", "content": message}
        st.session_state.chat_history.append(final_message)
        st.session_state.em_conversation_finished = True

# Add finish conversation button below chat input
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.em_conversation_finished and st.session_state.chat_history:
        if st.button("Finish Conversation", key="finish_em_conversation", use_container_width=True):
            st.session_state.em_conversation_finished = True
            session_id = log_transcript(
                st.session_state["mongodb_uri"],
                "em",
                st.session_state.chat_history
            )
            st.session_state.session_id = session_id
            st.rerun()