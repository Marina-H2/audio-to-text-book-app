import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import whisper
from pydub import AudioSegment
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac'}

# Load Whisper model
model = whisper.load_model("base")  # You can choose different model sizes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', extracted_text=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Process uploaded file or recorded audio
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Convert audio to text using Whisper
            text = process_audio(file_path)
            print("Extracted Text: ", text)  # For debugging
            
            # Use Selenium to fill out a form (example URL)
            if text:
                fill_form_automatically(text)
            
            return render_template('index.html', extracted_text=text)

    # Process recorded audio
    elif 'recordedAudio' in request.form:
        audio_data = request.form['recordedAudio']
        audio = BytesIO(bytes(audio_data.split(',')[1], 'utf-8'))  # Convert from base64
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'recorded_audio.wav')
        
        with open(file_path, 'wb') as f:
            f.write(audio.read())
        
        text = process_audio(file_path)
        print("Extracted Text from Recording: ", text)  # For debugging
        
        if text:
            fill_form_automatically(text)

        return render_template('index.html', extracted_text=text)

    return render_template('index.html', extracted_text="No file uploaded")

def process_audio(audio_path):
    # Use Whisper to transcribe the audio
    try:
        result = model.transcribe(audio_path)
        return result['text']
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

def fill_form_automatically(text):
    # Configure Selenium WebDriver options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    
    # Use appropriate path to your WebDriver executable
    service = Service('/path/to/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("http://example.com/your-form-url")  # Change to actual form URL
        # Example of filling a text input field
        text_input = driver.find_element(By.NAME, 'your-input-name')  # Update with actual input name
        text_input.send_keys(text)

        # Submit the form (if necessary)
        submit_button = driver.find_element(By.NAME, 'submit')  # Update with actual submit button name
        submit_button.click()

    finally:
        driver.quit()  # Close the browser session

if __name__ == "__main__":
    app.run(debug=True)