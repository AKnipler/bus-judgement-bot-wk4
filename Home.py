import streamlit as st
from openai import OpenAI
from utils.mongodb import check_identifier

def is_identifier_valid():
    identifier = st.session_state.get("user_identifier", "").strip()
    if not identifier:
        return False
    return check_identifier(st.session_state["mongodb_uri"], identifier)

def setup():

    if "em_prompt" not in st.session_state: 
        with open("./prompts/GPT-Prompt-Week-4.txt", "r", encoding="utf-8") as file:
            emprompt = file.read()

        st.session_state["em_prompt"] = emprompt

    if "model" not in st.session_state:
        st.session_state["model"] = "gpt-4o-mini"

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if "response_counter" not in st.session_state:
        st.session_state["response_counter"] = 0

    if "mongodb_uri" not in st.session_state:
        st.session_state["mongodb_uri"] = st.secrets["MONGODB_CONNECTION_STRING"]

    if "em_conversation_finished" not in st.session_state:
        st.session_state["em_conversation_finished"] = False

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = None

    if "user_identifier" not in st.session_state:
        st.session_state["user_identifier"] = ""

    # Set up OpenAI API client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    return client

def init_page():
    setup()
    st.title("Homepage (Week 4)")
    st.markdown(
        "Welcome! For this activity, you will interact with Em again, a middle manager in a mid-sized firm who often investigates issues for the CEO and helps shape executive judgement. " \
        "The aim is to practise making and justifying business judgements using techniques from the Cracked It textbook (Chapters 1, 2, 3, 4 and 5) and other subject materials." \
    )
    st.markdown(
        "## Instructions\n"
        "1. Enter your unique identifier below (the same one that you used last week). This will be used to associate your conversation records with you.\n"
        "2. In the Em Conversation tab, converse with Em (top left corner of the screen). Only when you are finished the conversation click the `finish` button. You will not be able to undo this submission.\n"
        "\nNote: Please ensure you have a stable internet connection to prevent any issues from occurring."
    )

    # Add identifier input after welcome message
    identifier = st.text_input(
        "Please enter your unique identifier:",
        key="identifier_input",
        value=st.session_state.get("user_identifier", ""),
        help="This identifier will be stored with your conversation records"
    )

    if identifier:
        if check_identifier(st.session_state["mongodb_uri"], identifier):
            st.session_state["user_identifier"] = identifier
            st.success("✅ Identifier validated successfully. You can now proceed to the conversation page.")
        else:
            st.error("❌ Invalid identifier. Please enter a valid identifier.")
            st.session_state["user_identifier"] = ""
    else:
        st.warning("⚠️ Please enter your identifier before starting any conversations.")

if __name__ == "__main__":
    init_page()


