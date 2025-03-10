from flask import Flask, render_template, request, jsonify
import os
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

def extract_audio_from_video(video_path, audio_path):
    """
    Extract audio from video and save it as a WAV file.
    """
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def transcribe_audio(audio_path):
    """
    Transcribe the audio file using Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="bn-BD")  # Bengali language
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"Error with Google Speech Recognition service: {e}"

def calculate_wpm(text, duration_minutes):
    """
    Calculate words per minute (WPM) based on the transcribed text and audio duration.
    """
    word_count = len(text.split())
    wpm = word_count / duration_minutes
    return wpm

@app.route('/')
def index():
    """
    Render the homepage where the user can upload a video.
    """
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    Handle the video upload, audio extraction, transcription, and WPM calculation.
    """
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.mp4'):
        # Save the uploaded video file
        video_path = os.path.join('uploads', file.filename)
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        file.save(video_path)

        # Step 1: Extract audio from the video
        audio_path = "extracted_audio.wav"
        extract_audio_from_video(video_path, audio_path)

        # Step 2: Transcribe the audio
        transcription = transcribe_audio(audio_path)

        # Step 3: Calculate Words Per Minute (WPM)
        if transcription:
            audio = AudioSegment.from_file(audio_path)
            duration_minutes = len(audio) / (1000 * 60)  # Convert milliseconds to minutes
            wpm = calculate_wpm(transcription, duration_minutes)
        else:
            wpm = 0

        # Clean up the temporary audio file
        os.remove(audio_path)

        # Return the result as HTML
        return render_template('result.html', transcription=transcription, wpm=wpm)

    return "Invalid file format. Only .mp4 files are allowed.", 400

if __name__ == "__main__":
    app.run(debug=True)
