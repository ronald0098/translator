import os
import openai
import whisper
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file
from moviepy.editor import VideoFileClip
import whisper
from googletrans import Translator
from gtts import gTTS 
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.editor import *
import json
import shutil  # Import shutil module for file operations

app = Flask(__name__)
app.config['static'] = 'static'

if app.debug:
    app.add_url_rule('/static/styles.css', 'static', build_only=True)


supported_languages = [
    "English","Hindi","Malayalam","Marathi","Tamil","Gujarati","Telugu","Kannada"
]

language_mapping = {
    "English": "en",
    "Hindi":"hi",
    "Malayalam":"ml",
    "Marathi":"mr",
    "Tamil":"ta",
    "Gujarati":"gu",
    "Telugu":"te",
    "Kannada":"kn"
    # Add more languages as needed
}

@app.route('/')
def index():
    return render_template('index.html', supported_languages=supported_languages)


@app.route('/uploadPage', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file given"
        
        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        # Handle file processing (e.g., translation)
        # Assuming translate_video is a function to process the video file
        if file:
            print(file)
            target_language_name = request.form.get('language')

            target_language_code = language_mapping.get(target_language_name, 'en')

            video_path = translate_video(file, target_language_code)
        
        # Return the translated video file as an attachment
        return send_file(video_path, as_attachment=True)

    # If the request method is GET, render the upload form
    return render_template('upload.html', supported_languages=supported_languages)
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    print(audio_path)
    result = model.transcribe(audio_path)
    #print(result)
    return result["text"]

def translate_video(submit_file, target_language):

    current_directory = os.getcwd()

    file_path = os.path.join(current_directory, "temp.mp4")

    # Save the uploaded file to the local directory
    submit_file.save(file_path)

    try:
        # Load the Whisper model and transcribe audio
        transcribed_text = transcribe_audio(file_path)
        
        # Translate the text using the Google Translate Library and target language
        translator = Translator()
        translated_text = translator.translate(transcribed_text, src="en", dest=target_language).text

        # Save the translated text to a file for reference (maybe subtitles in the future)
        with open("translated.txt", "w", encoding="utf-8") as f:
            f.write(translated_text)

        # Translate the audio into the selected language and save as mp3
        translated_audio = gTTS(text=translated_text, lang=target_language, slow=False)
        translated_audio.save("updated_audio.mp3") 
        translated_audio = AudioFileClip("updated_audio.mp3") 

        # Take the original video and put the new audio over it
        video = VideoFileClip(file_path)
        video = video.set_audio(translated_audio)

        # Define the path to save the translated video
        video_path = os.path.join(current_directory, "static", "result.mp4")
        
        # Write the video to the defined path
        video.write_videofile(video_path)
        
    finally:
        # Close the file after using it
        video.close()
        
    return video_path

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')




