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
SPEAK_TO_HUMAN_TEXT = "It appears that you mentioned a very serious topic (i.e., suicide, inflict harm on your self and others, violence) in conversation and I recommend reaching out to a human therapist."
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
        if keyword in prompt:
            return True
    return False


# setting OpenAI's ChatGPT API
import os
import openai

openai_client = openai.OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)

def chatgpt(prompt: str, context: str = "You are a helpful assistant.", model: str = "gpt-3.5-turbo") -> str:
    response = openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": context,
            },
             {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
    )
    return response.choices[0].message.content

# identification function powered by LLMs
def identify_user(prompt: str) -> tuple[str, str]:
    """
    From the prompt, figure out the name and gender of the user
    """
    return "Albert", "male"

# custom assistant for therapy with memory
def assistant(prompt: str, context: str = "You are a helpful assistant.") -> str:
    return "Not Programmed Yet!"

context = ""




### WEBSITE CODE ###
# safety variable
if "speak_to_human" not in st.session_state: st.session_state.speak_to_human = False

# keep track of user information (name and gender)
if "user_name" not in st.session_state: st.session_state.user_name = None
if "user_gender" not in st.session_state: st.session_state.user_gender = None

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": (
                "Hello, I'm Arpi, your AI therapist! "
                "I'm here to support you on your journey on mental well-being. "
                "Before we begin, what is your name and preferred pronouns? "
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
            # only check if response is dangerous if `speak_to_human` is false; otherwise default to seeking human therapist for every conversation afterwards
            if not st.session_state.speak_to_human:
                st.session_state.speak_to_human = extreme_serious_input(prompt)
            
            # give AI assistant response if `speak_to_human` is false
            if st.session_state.speak_to_human:
                response = SPEAK_TO_HUMAN_TEXT
            else:
                response = custom_assistant(prompt, context)
            
            # write response
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
