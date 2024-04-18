import requests
import random
from datetime import datetime
import time

# URL основного Flask-приложения
MAIN_APP_URL = 'http://localhost:5000'
# ID пациента для отправки данных
PATIENT_ID = '661ffbd88f30fcefe5d8fbba'

def send_data():
    while True:
        # Генерация случайных данных для сердечного ритма
        heart_rate = random.randint(60, 100)
        timestamp = datetime.now().isoformat()

        # Формирование JSON-запроса
        data = {
            'patient_id': PATIENT_ID,
            'heart_rate': heart_rate,
            'timestamp': timestamp
        }

        # Отправка POST-запроса на основное приложение
        response = requests.post(f"{MAIN_APP_URL}/receive_heart_rate_data/{PATIENT_ID}", json=data)
        print(response.text)

        time.sleep(5)

if __name__ == '__main__':
    send_data()
