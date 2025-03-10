from flask import Flask, render_template, request, jsonify
import os
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment
import time

app = Flask(__name__)

def convert_to_wav(input_audio_path):
    """
    Convert mp3, m4a to wav if necessary.
    """
    output_audio_path = "converted_audio.wav"
    
    try:
        audio = AudioSegment.from_file(input_audio_path)
        audio.export(output_audio_path, format="wav")
        return output_audio_path
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

def extract_audio_from_video(video_path):
    """
    Extract audio from video and save it as a WAV file.
    """
    audio_path = "extracted_audio.wav"
    try:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        video.close()  # Ensure the video file is properly closed
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

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
    wpm = word_count / duration_minutes if duration_minutes > 0 else 0
    return wpm

@app.route('/')
def index():
    """
    Render the homepage where the user can upload a file.
    """
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    Handle file upload, audio extraction/conversion, transcription, and WPM calculation.
    """
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Allowed file extensions
    allowed_extensions = ('.mp4', '.mp3', '.wav', '.m4a')
    
    if file and file.filename.endswith(allowed_extensions):
        # Save the uploaded file
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        # Add a small delay to ensure file is fully saved and closed
        time.sleep(1)  # Sleep for 1 second

        # Process based on file type
        if file.filename.endswith('.mp4'):
            audio_path = extract_audio_from_video(file_path)
        else:
            audio_path = convert_to_wav(file_path) if not file.filename.endswith('.wav') else file_path

        if not audio_path:
            return "Error processing audio file.", 500

        # Step 2: Transcribe the audio
        transcription = transcribe_audio(audio_path)

        # Step 3: Calculate Words Per Minute (WPM)
        if transcription:
            audio = AudioSegment.from_file(audio_path)
            duration_minutes = len(audio) / (1000 * 60)  # Convert milliseconds to minutes
            wpm = calculate_wpm(transcription, duration_minutes)
        else:
            wpm = 0

        # Clean up temporary files with a brief delay to ensure proper closure
        time.sleep(1)  # Sleep for 1 second to ensure the file is closed
        os.remove(audio_path)
        os.remove(file_path)

        # Return the result as HTML
        return render_template('result.html', transcription=transcription, wpm=wpm)

    return "Invalid file format. Only .mp4, .mp3, .wav, .m4a files are allowed.", 400

if __name__ == "__main__":
    app.run(debug=True)
