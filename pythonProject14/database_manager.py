# database_manager.py - модуль для работы с базой данных

from pymongo import MongoClient
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['medical_system']
        self.patients_collection = self.db['patients']
        self.doctors_collection = self.db['doctors']
        self.heart_rate_collection = self.db['heart_rate_sensor_data']
        self.temperature_collection = self.db['temperature_sensor_data']  # Замена коллекции на температуру тела

    def register_doctor(self, doctor_id, doctor_password):
        self.doctors_collection.insert_one({'_id': doctor_id, 'password': doctor_password})

    def register_patient(self, doctor_id, patient_name, patient_password, date_of_birth):
        try:
            datetime.strptime(date_of_birth, '%d.%m.%Y')
        except ValueError:
            return 'Неправильный формат даты рождения. Используйте формат dd.mm.yyyy'
        patient = {
            'name': patient_name,
            'password': patient_password,
            'date_of_birth': date_of_birth,
            'vital_signs': [],
            'doctor_id': doctor_id
        }
        self.patients_collection.insert_one(patient)
        return patient

    def find_doctor(self, doctor_id, doctor_password):
        return self.doctors_collection.find_one({'_id': doctor_id, 'password': doctor_password})

    def find_patient(self, patient_id, patient_password):
        return self.patients_collection.find_one({'_id': patient_id, 'password': patient_password})

    def get_patients_for_doctor(self, doctor_id):
        return list(self.patients_collection.find({'doctor_id': doctor_id}))

    def receive_temperature_data(self, patient_id, data):
        data['timestamp'] = datetime.now().isoformat()
        self.temperature_collection.insert_one({'patient_id': patient_id, 'data': data})
        return {'status': 'success'}  # Возвращаем словарь, а не jsonify, так как этот метод не возвращает HTTP-ответ

    def receive_heart_rate_data(self, patient_id, data):
        data['timestamp'] = datetime.now().isoformat()
        self.heart_rate_collection.insert_one({'patient_id': patient_id, 'data': data})
        return {'status': 'success'}  # Возвращаем словарь, а не jsonify, так как этот метод не возвращает HTTP-ответ

    def find_patient_by_id(self, patient_id):
        return self.patients_collection.find_one({'_id': patient_id})

    def get_temperature_data(self, patient_id):
        return list(self.temperature_collection.find({'patient_id': patient_id}))

    def get_heart_rate_data(self, patient_id):
        return list(self.heart_rate_collection.find({'patient_id': patient_id}))
