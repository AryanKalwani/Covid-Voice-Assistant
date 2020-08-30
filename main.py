import requests
import pyttsx3
import speech_recognition as sr
import json
import re
import threading
import time

API_KEY = "tG4y_bFWTR10"
PROJECT_TOKEN = "ta95BiFWER_d"
RUN_TOKEN = "tDRNiWuYaxTR"

response = requests.get(
    f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key": API_KEY})
data = json.loads(response.text)


class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.get_data()

    def get_total_cases(self):
        data = self.data['total']

        for text in data:
            if text['name'] == 'Coronavirus Cases:':
                return text['value']
        return '0'

    def get_data(self):
        response = requests.get(
            f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key": API_KEY})
        self.data = json.loads(response.text)

    def get_total_deaths(self):
        data = self.data['total']

        for text in data:
            if text['name'] == 'Deaths:':
                return text['value']
        return '0'

    def get_country_data(self, country):
        data = self.data['country']

        for text in data:
            if text['name'].lower() == country.lower():
                return text
        return '0'

    def get_list_of_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower())

        return countries

    def update_data(self):
        response = requests.post(
            f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data updated")
                    break
                time.sleep(5)

            t = threading.Thread(target=poll)
            t.start()


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))
    return said.lower()


def main():

    print("Initiating the program")
    END_PHRASE = "stop"
    data = Data(API_KEY, PROJECT_TOKEN)
    country_list = (data.get_list_of_countries())
    UPDATE_COMMAND = "update"

    TOTAL_PATTERNS = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total [\w\s]+ death"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total death"): data.get_total_deaths

    }

    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
    }

    while True:
        print('Listening...')
        text = get_audio()
        result = None
        print(text)

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break

        if text == UPDATE_COMMAND:
            result = "Data is being updated. This may take a moment!"
            data.update_data()

        if result:
            print(result)
            speak(result)

        if text.find(END_PHRASE) != -1:
            break


main()
