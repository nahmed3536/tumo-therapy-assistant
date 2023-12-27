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
# handling extreme dangerous or trickly situations by redirecting to speaking a human therapist
SPEAK_TO_HUMAN = False
SPEAK_TO_HUMAN_TEXT = "It appears you are discussing a very serious topic (i.e., suicide, inflict harm on your self and others, violence) and I recommend reaching out to a human therapist."
def extreme_serious_input(prompt: str) -> bool:
    """
    It will analyze the prompt for any extreme serious key words and make discussion come to a close
    """
    keywords = [
        "death", 
        "suicide",
        "harm",
        "kill",
        "attack",
    ]
    for keyword in keywords:
        if keywords in prompt:
            return True
    return False


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
            # only check if response is dangerous if SPEAK_TO_HUMAN is false; otherwise default to seeking human therapist for every conversation afterwards
            if SPEAK_TO_HUMAN == False:
                SPEAK_TO_HUMAN = extreme_serious_input(prompt)
            
            # give AI assistant response if SPEAK_TO_HUMAN is false
            if SPEAK_TO_HUMAN == True:
                response = SPEAK_TO_HUMAN_TEXT
            else:
                response = custom_assistant(prompt, context)
            
            # write response
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
