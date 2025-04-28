from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import os
import difflib
from datetime import datetime

app = Flask(__name__)  # ✅ fixed here
UPLOAD_FOLDER = 'recordings'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_similarity(user_text, expected_text):
    similarity = difflib.SequenceMatcher(None, user_text.lower(), expected_text.lower()).ratio()
    return round(similarity * 100, 2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    audio = request.files['audio_data']
    expected = request.form['expected_text']

    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".wav"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    audio.save(filepath)

    recognizer = sr.Recognizer()
    text = ""
    score = 0

    with sr.AudioFile(filepath) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            score = get_similarity(text, expected)
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio'})
        except sr.RequestError:
            return jsonify({'error': 'Speech recognition failed'})

    if score >= 80:
        feedback = "Great job! Your pronunciation is very clear."
    elif score >= 50:
        feedback = "Not bad, but you can improve your pronunciation."
    else:
        feedback = "Try again, focus on the pronunciation of each word."

    return jsonify({
        'transcription': text,
        'expected': expected,
        'score': score,
        'feedback': feedback
    })

if __name__ == '__main__':  # ✅ fixed here
    app.run(debug=True)