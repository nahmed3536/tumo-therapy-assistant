import streamlit as st

### PAGE CONFIGURATION ###
# set the page / tab title
st.set_page_config(page_title="Arpi Therapy")

# set the header
st.header("Arpi Therapy")



### CORE FUNCTIONALITY ###
# access toml configuration
import toml
config = toml.load(".streamlit/config.toml")



### AI ASSISTANT CODE ###
def assistant(prompt: str, context: str = "You are a helpful assistant.") -> str:
    return "Not Programmed Yet!"

context = ""




### WEBSITE CODE ###
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": (
                "Hello, I'm Arpi, your AI therapist! "
                "I'm here to support you on your journey on "
                "mental well-being. How are you feeling today? "
            )
        }
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=config["custom"]["assistant_avatar"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=config["custom"]["assistant_avatar"]):
        with st.spinner("Thinking..."):
            response = assistant(prompt, context)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
