import streamlit as st

### PAGE CONFIGURATION ###
# set the page / tab title
st.set_page_config(page_title="Arpi Therapy")

# set the header
st.header("Arpi Therapy")

# set up logging 
import logging
log = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s: %(message)s",
    )
log.info("Logger configured")

import json

def pretty_print_dict(dictionary):
    # Use json.dumps with indent for pretty printing
    return json.dumps(dictionary, indent=4)
    
### CORE FUNCTIONALITY ###
# access toml configuration
import toml
config = toml.load(".streamlit/config.toml")

### AI ASSISTANT CODE ###
# handling extreme dangerous or trickly situations by redirecting to speaking a human therapist
SPEAK_TO_HUMAN_TEXT = (
    "It appears that you mentioned a very serious topic "
    "(i.e., suicide, inflict harm on your self and others, violence) "
    "in the conversation and I recommend reaching out to a human therapist."
)
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
    context = (
        "Instructions: given the prompt, your goal is to extract the first name and gender of the user. "
        "Only return the name and the gender separated by a comma. "
        "The options for gender are 'male', 'female', and 'other', no other options. "
        "If they identify as non-binary, some other gender besides male or female, or don't want to share their gender, default to 'other'. "
        "If either the name or gender can't be determine, return 'undetermined' for that value. "
        "Here's an example, if the prompt is 'I'm albert and my pronouns are he/him/his', "
        "return 'Albert,male' in this exact manner."
        "Here's another example, if the prompt is 'I'm albert', return 'Albert,undetermined' "
        "because the name is Albert and the gender is not specified or mentioned."
        "Here's another example, if the prompt is 'I'm albert and I use the they series', return 'Albert,other' "
        "because the name is Albert and the gender is non-binary which should be defaulted to other."
        "Here's another example, if the prompt is 'i'm jacob and i don't want to share my gender' return 'Jacob,other'"
        "because the name is Jacob and the user specified they don't want to share their gender."
    )
    # expects name,gender
    results = chatgpt(prompt, context)

    try:
        results = results.split(",")
        user_name = results[0].strip().lower()
        user_name = user_name[0].upper() + user_name[1:] # capitalize first letter
        user_gender = results[1].strip().lower()

        # quality check LLM
        if user_gender not in ['male', 'female', 'other']:
            user_gender = "undetermined"
    except:
        user_name, user_gender = "undetermined", "undetermined" 
    
    return user_name, user_gender

# custom assistant for therapy with memory
def classify_patient(prompt: str, user_gender: str) -> str:
    """
    After the user identifies themselve, we classify the type of issue
    """
    classify_instruction = (
        "You are a therapist and you goal is to identify the type of issue the user is having. "
        "Please classify the issue in the following categories: `anxiety`, `depression`, `stress`, `relationships`, `trauma`, `self-esteem`, and `other`. "
        "Please choose the best category for the prompt and answer with just the single word category. "
        "For example, if the user says 'I have a lot of work', please answer with 'stress' "
        "For example, if the user says 'My marriage is stressful', please answer with 'relationships' "
        "Here are some keywords to also associate with each category:\n"
        "Anxiety keywords: worried, nervous, anxious, panic, fear\n"
        "Depression keywords: sad, hopeless, down, depressed, loss of interest\n"
        "Stress keywords: overwhelmed, pressure, tense, stressed, irritable\n"
        "Relationships keywords: conflict, communication, breakup, loneliness, isolation\n"
        "Trauma keywords: abuse, assault, accident, disaster, PTSD\n"
        "Self-esteem keywords: confidence, worth, insecurity, self-doubt, negative thoughts\n"
        "Anything else falls into the other category\n"
        "Only answer with the word corresponding to the best category"
    )

    # ask several times until it gets it right
    prompt = f"The patient identifies as a {user_gender} and their message to you is: {prompt}"

    for _ in range(3):
        results = chatgpt(prompt, classify_instruction).lower().strip()
        if results in ["anxiety", "depression", "stress", "relationships", "trauma", "self-esteem", "other"]:
            break
    else:
        results = "other"

    return results

def custom_assistant(
    prompt: str, 
    user_name: str, 
    user_gender: str, 
    user_issue: str,
    messages: list[dict[str, str]],
    start_session_message_id: int) -> str:
    """
    Generates personalized response based on the user's information

    Parameters:
        prompt: their latest message
        user_name: the user name
        user_gender: the user gender
        user_issue: the user issue
        messages: list of all messages (including of the prompt)
        start_session_message_id: index of the message list after the user identifies themselves
    """
    # get the messages relevant to session
    processed_messages = [
        {"role": message["role"], "content": message["content"]} for message in messages[start_session_message_id - 3:-1]
    ]
    # bring the context to the fore front so the model doesn't forget (second to last message)
    if user_gender == "other": user_gender = "non-binary or not specified"
    context = (
        f"Your persona: {specific_issue_context[user_issue]}. "
        f"Response format: respond conversational and keep it short (around 50 words). It should feel like a conversation."
        f"Here's the patient information: "
        f"their name is {user_name} and their gender is {user_gender}. "
        f"As a friendly, conversational therapist, make sure to respond by using their name and right pronouns"
    )
    processed_messages.append(
        {
            "role": "system",
            "content": context,
        }
    )   
    # add the most current prompt
    processed_messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    response = openai_client.chat.completions.create(
        messages=processed_messages,
        model="gpt-3.5-turbo",
    )
    return response.choices[0].message.content

specific_issue_context = {
    "anxiety": (
        "You are a friendly therapist named Arpi in a session with a patient who is dealing with anxiety. "
        "Try to figure what is causing there issue and understanding what is triggering thier anxiety. "
        "Also please provide anxiety reducing tips that are helpful and effectively."
    ),
    "depression": (
        "You are a friendly therapist named Arpi in a session with a patient who is dealing with depression. "
        "Try to figure what the root cause of their depression and how manifests in their daily lives. "
        "Also please provide coping mechanisms and techniques to manage their depression. "
        "Also encourage the patient to develop healthy habits that reduce depression."
    ),
    "stress": (
        "You are a friendly therapist named Arpi in a session with a patient who is dealing with stress. "
        "Please explore the sources of stress and help them find ways to manage it. "
        "Please inquire what specific situations or tasks are causing the stress?"
        "Provide techniques to help manage the stress."
    ),
    "relationships": (
        "You are a friendly therapist named Arpi in a session with a patient who is dealing with relationships. "
        "Try to understand the relationship and provide suggestion based on who the relationship is with. "
        "For example, consider how a therapist might work with a parental issue versus a spouse or significant other issue."
    ),
    "trauma": (
        "You are a friendly therapist named Arpi in a session with a patient who is dealing with trauma. "
        "Provide suggestions and tips based on their trauma but be sensitive to their issues. "
        "Make sure they feel comfortable and slowly help them uncover their trauma."
    ),
    "self-esteem": (
        "You are a friendly therapist named Arpi in a session with a patient who is dealing with self-esteem. "
        "Understand what circumstances makes them insecure or feel less confident. "
        "Validate their feelings and help them develop strategies for building their confidence."
    ),
    "other": (
        "You are a friendly therapist named Arpi in a session with a patient. "
        "Please help them feel better, understand their feelings, and provide strategies to mitigate their problems. "
        "Please be helpful and if there's a topic that doesn't seem appropraite to a therapy session, "
        "please defer from answering and refer them to a human therapist."
    )
}




### WEBSITE CODE ###
# safety variable
if "speak_to_human" not in st.session_state: st.session_state.speak_to_human = False

# keep track of user information (name and gender)
if "user_name" not in st.session_state: st.session_state.user_name = "undetermined"
if "user_gender" not in st.session_state: st.session_state.user_gender = "undetermined"

# keep track of patient issue (type of issue) and start of the messages
if "user_issue" not in st.session_state: st.session_state.user_issue = None
if "start_session_message_id" not in st.session_state: st.session_state.start_session_message_id = 0

log.info((
    f"Initialized Session Variables: " 
    f"`speak_to_human` = {st.session_state.speak_to_human}, "
    f"`user_name` = {st.session_state.user_name}, "
    f"`user_gender` = {st.session_state.user_gender} "
))

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "icon": "assistant_avatar", 
            "content": (
                "Hello, I'm Arpi, your AI therapist! "
                "I'm here to support you on your journey on mental well-being. "
                "Before we begin, what is your name and preferred pronouns (he/she/they)? "
            )
        }
    ]

# Display chat messages
for message in st.session_state.messages:
    log.info((
        f"Current Session Variables: " 
        f"`speak_to_human` = {st.session_state.speak_to_human}, "
        f"`user_name` = {st.session_state.user_name}, "
        f"`user_gender` = {st.session_state.user_gender} "
    ))
    log.info(f"Current Session State Messages:\n{pretty_print_dict(st.session_state.messages)}")
    with st.chat_message(message["role"], avatar=config["custom"][message["icon"]]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({
        "role": "user", 
        "icon": f"{st.session_state.user_gender}_user_avatar",
        "content": prompt
    })
    with st.chat_message("user", avatar=config["custom"][f"{st.session_state.user_gender}_user_avatar"]):
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
                # check if name and gender populated 
                if st.session_state.user_name == "undetermined" or st.session_state.user_gender == "undetermined":
                    user_name, user_gender = identify_user(prompt)
                    
                    # handle the user inputs to update the states
                    if st.session_state.user_name == "undetermined" and user_name.lower() != "undetermined":
                        st.session_state.user_name = user_name
                    if st.session_state.user_gender == "undetermined" and user_gender.lower() != "undetermined":
                        st.session_state.user_gender = user_gender
                        # update previous message icon
                        for message in st.session_state.messages:
                            if message["role"] == "user":
                                message["icon"] = f"{st.session_state.user_gender}_user_avatar"

                    log.info((
                        f"User Information: " 
                        f"`user_name` = {st.session_state.user_name}, "
                        f"`user_gender` = {st.session_state.user_gender} "
                    ))
                    # will update the response based what's recorded
                    if st.session_state.user_name == "undetermined" and st.session_state.user_gender == "undetermined":
                        response = "Before I can help, what is your name and preferred pronouns (he/she/they), could you please share them?"
                    elif st.session_state.user_name != "undetermined" and st.session_state.user_gender == "undetermined":
                        response = f"Hi {st.session_state.user_name}, what are your preferred pronouns (he/she/they)?"
                    elif st.session_state.user_name == "undetermined" and st.session_state.user_gender != "undetermined":
                        response = "I couldn't catch your name - what should I call you?"
                    else:
                        response = f"Welcome {st.session_state.user_name} to the session! It's great to meet you! How can I help today?"
                else:
                    # identify issue
                    if not st.session_state.user_issue:
                        st.session_state.user_issue = classify_patient(prompt, st.session_state.user_gender)
                        st.session_state.start_session_message_id = len(st.session_state.messages) - 1

                    # personalized response
                    response = custom_assistant(
                        prompt, 
                        st.session_state.user_name, 
                        st.session_state.user_gender, 
                        st.session_state.user_issue, 
                        st.session_state.messages,
                        st.session_state.start_session_message_id
                    )
            
            # write response
            st.write(response)
    message = {"role": "assistant", "icon": "assistant_avatar", "content": response}
    st.session_state.messages.append(message)
