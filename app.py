from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import moviepy.editor as mp
import speech_recognition as sr

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)

            video = mp.VideoFileClip(video_path)
            audio = video.audio
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.wav')
            audio.write_audiofile(audio_path)

            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)

            try:
                audio_text = recognizer.recognize_google(audio_data, language='ta-IN')
                subtitles = [subtitle.strip() for subtitle in audio_text.split('.')]
                return render_template('index.html', video_path=video_path, subtitles=subtitles)
            except sr.UnknownValueError:
                subtitles = ["Speech recognition could not understand the audio."]
                return render_template('index.html', video_path=video_path, subtitles=subtitles)

    return render_template('index.html', video_path=None, subtitles=None)

if __name__ == '__main__':
    app.run(debug=True)
