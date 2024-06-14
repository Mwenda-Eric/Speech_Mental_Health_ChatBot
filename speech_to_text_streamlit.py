import streamlit as st
import sounddevice as sd
import wavio
import speech_recognition as sr
import openai
import pyttsx3
import time
from tempfile import NamedTemporaryFile
import os

# Configure OpenAI API key
openai.api_key = st.secrets["OPEN_API_KEY"]

# Initialize pyttsx3 engine
# engine = pyttsx3.init()

def list_input_devices():
    """
    Lists available audio input devices.
    """
    devices = sd.query_devices()
    input_devices = [device for device in devices if device['max_input_channels'] > 0]
    return input_devices

def record_audio(record_seconds=5, rate=44100, device=0):
    """
    Records audio from the microphone and returns the filename.
    """
    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        filename = temp_audio_file.name
        print("Recording...")
        myrecording = sd.rec(int(record_seconds * rate), samplerate=rate, channels=1, device=device)
        sd.wait()  # Wait until recording is finished
        print("Finished recording.")
        wavio.write(filename, myrecording, rate, sampwidth=2)
    return filename

def transcribe_audio(filename):
    """
    Transcribes the given audio file using Google's speech recognition.
    """
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(filename)

    with audio_file as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        print("Transcription: " + text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def query_chatgpt(prompt):
    """
    Queries the OpenAI ChatGPT API with the provided prompt.
    """
    base_prompt = (
            "You are a helpful assistant specialized in mental health support. "
            "Your job is to provide advice, support, and information about mental health issues. "
            "You can address topics like stress, anxiety, depression, anger management, and general well-being. "
            "Please keep your responses focused on mental health and well-being.\n\n"
            "User: " + prompt + "\n"
                                "Assistant:"
    )

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",  # or "text-davinci-003" based on your available engines
        prompt=base_prompt,
        max_tokens=2500
    )
    message = response.choices[0].text.strip()
    print("ChatGPT Response: " + message)
    return message

def speak_text(text):
    """
    Uses pyttsx3 to convert text to speech.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine = None

st.title("Mental Health Chatbot")
st.subheader("Welcome! Please speak about your mental health, such as your thoughts and feelings. Our chatbot is here to listen and respond to you.")

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# List available input devices
input_devices = list_input_devices()
st.write("INPUT DEVICES FOUND:")
st.write(input_devices)
input_device_names = [f"{i}: {device['name']}" for i, device in enumerate(input_devices)]
selected_device_index = st.selectbox("Select input device", input_device_names, index=0)
device_id = int(selected_device_index.split(":")[0])

if st.button("Speak"):
    # Record audio from the microphone
    filename = record_audio(record_seconds=5, device=device_id)

    # Transcribe the recorded audio
    text = transcribe_audio(filename)

    if text:
        st.session_state.conversation.append(("user", text))

        # Query ChatGPT API
        response = query_chatgpt(text)
        st.session_state.conversation.append(("bot", response))

# Display the conversation
for speaker, message in st.session_state.conversation:
    if speaker == "user":
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.write(message)

# Speak out the latest response
if st.session_state.conversation and st.session_state.conversation[-1][0] == "bot":
    speak_text(st.session_state.conversation[-1][1])
