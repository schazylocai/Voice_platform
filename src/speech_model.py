import streamlit as st
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torchaudio
import subprocess
import time
import os
import json

# Caching the model and processor to load only once
@st.cache_resource
def load_model():
    """Load the model from a specified path if not already loaded."""
    model_path = "Whisper"
    if model_path == "Whisper":
        processor = WhisperProcessor.from_pretrained("openai/whisper-large-v3-turbo", language="Arabic", task="transcribe")
        model = WhisperForConditionalGeneration.from_pretrained('openai/whisper-large-v3-turbo').to("cpu")
    else:
        processor = WhisperProcessor.from_pretrained("openai/whisper-large-v3", language="Arabic", task="transcribe")
        model = WhisperForConditionalGeneration.from_pretrained('/models/' + model_path).to("cpu")
    model.eval()
    return processor, model

# Function to preprocess audio
def preprocess_audio(input_path, output_path):
    """
    Preprocesses the audio file to have 1 channel, 16 kHz sample rate, and checks duration.
    - Converts audio to 1 channel and 16 kHz using ffmpeg.
    - Returns False if the audio exceeds 30 seconds, True otherwise.
    """
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = float(result.stdout.strip())

        if duration > 30:
            return False, "Audio file exceeds 30 seconds limit."

        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ac", "1", "-ar", "16000", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return True, "Audio processed successfully."
    except Exception as e:
        return False, f"Error processing audio: {str(e)}"

# Streamlit UI
def start_transcribing():
    st.title(":violet[Mira Speech to Text]")
    st.subheader(":violet[Upload an audio file to transcribe.]")

    uploaded_file = st.file_uploader("Choose an audio file",
                                     type=["wav", "mp3", "m4a"],
                                     label_visibility='collapsed')

    if uploaded_file is not None:
        input_path = f"/tmp/{uploaded_file.name}"
        output_path = "/tmp/preprocessed_audio.wav"

        # Save uploaded file to disk
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Preprocess audio
        success, message = preprocess_audio(input_path, output_path)
        if not success:
            st.error(message)
            return
        else:
            st.success(message)

        # Load model
        with st.spinner('Loading model...'):
            processor, model = load_model()

        # Transcribe
        audio_input, sampling_rate = torchaudio.load(output_path)
        audio_input = audio_input.squeeze().numpy()

        if sampling_rate != 16000:
            st.error("Audio file does not have the correct sampling rate of 16 kHz.")
            return

        inputs = processor(audio_input, sampling_rate=16000, return_tensors="pt")
        inputs = inputs.to("cpu")

        start_time = time.time()
        with torch.no_grad():
            predicted_ids = model.generate(inputs.input_features)
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        latency = time.time() - start_time

        # Display results
        st.write("### Transcription:")
        st.text_area("", transcription, height=200)
        st.write(f"**Latency:** {latency:.2f} seconds")

start_transcribing()