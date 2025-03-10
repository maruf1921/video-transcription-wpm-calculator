# Video to Bengali Text Transcription and WPM Calculator

This web application allows users to upload a video or audio file (MP4, MP3), extract its audio, transcribe the audio into Bengali text, and calculate the words per minute (WPM) based on the transcription. The application is built using **Flask** for the backend and utilizes libraries like **moviepy**, **SpeechRecognition**, and **pydub** for audio processing and transcription.

## Features
- Upload a video (MP4) or audio (MP3) file.
- Extract audio from video if the file is in MP4 format.
- Transcribe the extracted audio into Bengali text.
- Calculate and display the words per minute (WPM) based on the transcription.

## Requirements

Before running the app, make sure to install the necessary libraries and dependencies:

```bash
pip install Flask
pip install moviepy==1.0.3
pip install SpeechRecognition
pip install pydub
python app.py

