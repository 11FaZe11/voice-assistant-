import sys
import speech_recognition as sr  # type: ignore
import pyttsx3
import pywhatkit  # type: ignore
import datetime
import pyjokes
import numpy as np  # type: ignore
from googlesearch import search  # type: ignore
import requests
from bs4 import BeautifulSoup
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer
import http.client
import json

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def talk(text):
    engine.say(text)
    engine.runAndWait()

def introduce_orion():
    talk("Hello, I am Orion, your personal assistant. How can I help you today?")

def update_volume_bar(volume, volume_bar):
    volume_bar.setFixedHeight(int(volume * 300))

def take_command(volume_bar):
    command = ""
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source, timeout=5)

            audio_data = np.frombuffer(voice.get_raw_data(), np.int16)
            rms = np.sqrt(np.mean(audio_data**2))
            normalized_rms = rms / 32768.0

            update_volume_bar(normalized_rms, volume_bar)

            command = listener.recognize_google(voice, language='en')
            command = command.lower()
            if 'Orion' in command:
                command = command.replace('Orion', '')
                print(command)
            else:
                command = listener.recognize_google(voice, language='ar')
                command = command.lower()
                if 'أوريون' in command:
                    command = command.replace('أوريون', '')
                    print(command)
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that.")
        talk("Sorry, I didn't understand that.")
    except sr.RequestError:
        print("Sorry, the speech recognition service is unavailable.")
        talk("Sorry, the speech recognition service is unavailable.")
    return command

def google_search(query):
    try:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        talk('Performing a Google search for ' + query)
        search_results = search(query, num_results=1)
        if search_results:
            first_result = search_results[0]
            talk(f"The first search result is {first_result}")
            talk("Fetching a description for the result.")

            response = requests.get(first_result)
            soup = BeautifulSoup(response.text, 'html.parser')

            paragraphs = soup.find_all('p')
            if paragraphs:
                description = " ".join([p.get_text() for p in paragraphs[:3]])
                if len(description) > 500:
                    description = description[:500] + '...'  # Trim if too long
                talk(f"Description of the result: {description}")
            else:
                talk("Could not retrieve a description for the result.")
        else:
            talk("No results were found.")
    except Exception as e:
        talk("An error occurred while trying to fetch the result description.")
        print(f"Error: {e}")

def ask_chatgpt(question):
    conn = http.client.HTTPSConnection("cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com")
    payload = json.dumps({
        "messages": [{"role": "user", "content": question}],
        "model": "gpt-4o",
        "max_tokens": 100,
        "temperature": 0.9
    })
    headers = {
        'x-rapidapi-key': "352934ff03msh4437f4260268d52p1b1b89jsn127a5cb4a37d",
        'x-rapidapi-host': "cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read()
    response = json.loads(data.decode("utf-8"))
    return response['choices'][0]['message']['content']

def run_Orion(command, volume_bar):
    if 'play' in command or 'تشغيل' in command or 'اغنية' in command:
        song = command.replace('play', '').replace('تشغيل', '').replace('اغنية', '').strip()
        if song:
            talk('Playing ' + song)
            pywhatkit.playonyt(song)
        else:
            talk('What song would you like to play?')
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk('The current time is ' + time)
    elif 'do you know' in command:
        query = command.replace('do you know', '').strip()
        if query:
            google_search(query)
        else:
            talk('What would you like to search for?')
    elif 'search for' in command:
        query = command.replace('search for', '').strip()
        if query:
            google_search(query)
        else:
            talk('What would you like to search for?')
    elif 'ask chatgpt' in command:
        question = command.replace('ask chatgpt', '').strip()
        if question:
            response = ask_chatgpt(question)
            talk(response)
        else:
            talk('What would you like to ask ChatGPT?')
    elif 'date' in command:
        talk('Sorry, I have a headache.')
    elif 'are you single' in command:
        talk('I am in a relationship with Wi-Fi.')
    elif 'joke' in command:
        talk(pyjokes.get_joke())
    elif 'facebook' in command:
        talk('Opening Facebook.')
        webbrowser.open('https://www.facebook.com')
    elif 'whatsapp' in command:
        talk('Opening WhatsApp.')
        webbrowser.open('https://web.whatsapp.com')
    elif 'instagram' in command:
        talk('Opening Instagram.')
        webbrowser.open('https://www.instagram.com')
    elif 'youtube' in command:
        talk('Opening Youtube.')
        webbrowser.open('https://www.youtube.com/')
    elif 'chatgpt' in command:
        talk('Opening ChatGPT.')
        webbrowser.open('https://chatgpt.com/?model=auto/')
    elif 'how are you' in command:
        talk("I'm good, and you?")
        user_reply = take_command(volume_bar)
        if 'good' in user_reply or 'fine' in user_reply:
            talk("You deserve all the best.")
        else:
            talk("I hope you feel better soon.")
    else:
        talk('Please repeat the command.')

class OrionAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Orion Personal Assistant")
        self.setGeometry(100, 100, 1188, 1177)
        self.setWindowIcon(QIcon("Images_icon/Orion.png"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        logo_label = QLabel()
        logo_pixmap = QPixmap("Images_icon/alexa_logo.png")
        logo_label.setPixmap(logo_pixmap)
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        self.entry = QLineEdit(self)
        self.entry.setPlaceholderText("Enter your command here...")
        layout.addWidget(self.entry)

        search_button = QPushButton("Search", self)
        search_button.clicked.connect(self.on_search)
        layout.addWidget(search_button)

        voice_button = QPushButton("Voice Search", self)
        voice_button.clicked.connect(self.on_voice_search)
        layout.addWidget(voice_button)

        self.volume_bar = QFrame(self)
        self.volume_bar.setFrameShape(QFrame.StyledPanel)
        self.volume_bar.setFixedSize(50, 300)
        layout.addWidget(self.volume_bar, alignment=Qt.AlignCenter)

        toggle_lang_button = QPushButton("Toggle Language", self)
        toggle_lang_button.clicked.connect(self.toggle_language)
        layout.addWidget(toggle_lang_button)

        quick_commands = [
            ("ChatGPT", "Images_icon/chatgpt (2).png", lambda: run_Orion("chatgpt", self.volume_bar)),
            ("Time", "Images_icon/time.png", lambda: run_Orion("time", self.volume_bar)),
            ("Joke", "Images_icon/joke.png", lambda: run_Orion("joke", self.volume_bar)),
            ("Facebook", "Images_icon/facebook.png", lambda: run_Orion("facebook", self.volume_bar)),
            ("WhatsApp", "Images_icon/whatsapp.png", lambda: run_Orion("whatsapp", self.volume_bar)),
            ("Instagram", "Images_icon/instagram.png", lambda: run_Orion("instagram", self.volume_bar)),
            ("YouTube", "Images_icon/youtube.png", lambda: run_Orion("youtube", self.volume_bar)),
            ("Instagram", "Images_icon/instagram .png", lambda: run_Orion("instagram", self.volume_bar))
        ]

        for text, icon_path, command in quick_commands:
            btn = QPushButton(self)
            btn.setIcon(QIcon(icon_path))
            btn.clicked.connect(command)
            layout.addWidget(btn)

        QTimer.singleShot(1000, introduce_orion)

        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 18px;
            }
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #ecf0f1;
                padding: 5px;
                font-size: 16px;
            }
            QPushButton {
                background-color: #2980b9;
                color: #ecf0f1;
                border: none;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QFrame {
                background-color: #34495e;
            }
        """)

    def on_search(self):
        command = self.entry.text()
        run_Orion(command, self.volume_bar)

    def on_voice_search(self):
        command = take_command(self.volume_bar)
        self.entry.setText(command)
        run_Orion(command, self.volume_bar)

    def toggle_language(self):
        global current_language
        if current_language == 'en':
            current_language = 'ar'
            talk("Language switched to Arabic")
        else:
            current_language = 'en'
            talk("Language switched to English")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OrionAssistant()
    ex.show()
    sys.exit(app.exec_())