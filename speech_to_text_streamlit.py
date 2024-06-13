import streamlit as st

def speak_text_js(text):
    """
    Generates JavaScript code for browser-based text-to-speech.
    """
    return f"""
    <script>
    var msg = new SpeechSynthesisUtterance();
    msg.text = "{text}";
    window.speechSynthesis.speak(msg);
    </script>
    """

st.title("Text-to-Speech Test")
st.subheader("Click the button to hear the text.")

# Create a button to trigger the text-to-speech
if st.button("Speak"):
    # Hardcoded text to speak
    text = "Hello, this is me. My name is Eric."

    # Inject JavaScript for text-to-speech
    st.markdown(speak_text_js(text), unsafe_allow_html=True)
