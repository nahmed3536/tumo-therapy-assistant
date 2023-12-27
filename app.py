import streamlit as st

### PAGE CONFIGURATION ###
# set the page / tab title
st.set_page_config(page_title="Arpi Therapy")

# set the header
st.header("Arpi Therapy")

### PAGE CONFIGURATION ###

### AI ASSISTANT CODE ###
def assistant(prompt: str, context: str = "You are a helpful assistant.") -> str:
    return "Not Programmed Yet!"

context = ""

### AI ASSISTANT CODE ###


### WEBSITE CODE ###
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = assistant(prompt, context)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
### WEBSITE CODE ###