import os
from time import time
import asyncio
from typing import Union
import streamlit as st
from dotenv import load_dotenv
import openai
from deepgram import Deepgram
import elevenlabs
from record import speech_to_text

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
elevenlabs.set_api_key(os.getenv("ELEVENLABS_API_KEY"))

# Initialize APIs
# gpt_client = openai.Client(api_key=OPENAI_API_KEY)
openai.api_key = OPENAI_API_KEY
deepgram = Deepgram(DEEPGRAM_API_KEY)

context = "You are Jarvis, Dhyan's human assistant. You are witty and full of personality. Your answers should be limited to 1-2 short sentences."
conversation = {"Conversation": []}
RECORDING_PATH = "audio/recording.wav"


def request_gpt(prompt: str) -> str:
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=f"{prompt}",
    )
    return response.choices[0].text.strip()


async def transcribe(file_name: Union[Union[str, bytes], int]) -> str:
    with open(file_name, "rb") as audio:
        source = {"buffer": audio, "mimetype": "audio/wav"}
        response = await deepgram.transcription.prerecorded(source)
        return response["results"]["channels"][0]["alternatives"][0]["words"]


def main():
    global context
    st.title("Jarvis")

    start_button = st.button("Start Listening")
    stop_button = st.button("Stop Listening")
    # Use empty placeholder for dynamic updating
    output_placeholder = st.empty()

    while start_button:
        st.write("Listening...")
        speech_to_text()
        st.write("Done listening")

        current_time = time()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        words = loop.run_until_complete(transcribe(RECORDING_PATH))
        string_words = " ".join(word_dict.get("word") for word_dict in words if "word" in word_dict)

        with open("conv.txt", "a") as f:
            f.write(f"{string_words}\n")

        transcription_time = time() - current_time
        st.write(f"Finished transcribing in {transcription_time:.2f} seconds.")

        current_time = time()
        context += f"\nAlex: {string_words}\nJarvis: "
        response = request_gpt(context)
        context += response
        gpt_time = time() - current_time
        st.write(f"Finished generating response in {gpt_time:.2f} seconds.")

        current_time = time()
        audio = elevenlabs.generate(text=response, voice="Adam", model="eleven_monolingual_v1")
        elevenlabs.save(audio, "audio/response.wav")
        audio_time = time() - current_time
        st.write(f"Finished generating audio in {audio_time:.2f} seconds.")

        st.write("Speaking...")
        st.audio("audio/response.wav")

        with open("conv.txt", "a") as f:
            f.write(f"{response}\n")

        st.write(f"\n --- USER: {string_words}\n --- JARVIS: {response}\n")

        # Update placeholder with the current content
        output_placeholder.text("Listening... Press 'Stop Listening' to stop.")
        

    if stop_button:
        st.write("Listening stopped.")


if __name__ == "__main__":
    main()
