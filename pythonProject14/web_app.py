from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from datetime import datetime
import plotly.graph_objs as go
from bson import ObjectId


class WebApp:
    def __init__(self, app):
        self.app = app
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['medical_system']
        self.patients_collection = self.db['patients']
        self.doctors_collection = self.db['doctors']
        self.heart_rate_collection = self.db['heart_rate_sensor_data']
        self.temperature_collection = self.db['temperature_sensor_data']  # Замена коллекции на температуру тела

        self.register_routes()

    def register_routes(self):
        self.app.route('/')(self.index)
        self.app.route('/register_doctor', methods=['GET', 'POST'])(self.register_doctor)
        self.app.route('/register_patient', methods=['GET', 'POST'])(self.register_patient)
        self.app.route('/login', methods=['POST'])(self.login)
        self.app.route('/doctor_login')(self.doctor_login)
        self.app.route('/doctor_dashboard')(self.doctor_dashboard)
        self.app.route('/receive_temperature_data/<patient_id>', methods=['POST'])(self.receive_temperature_data)
        self.app.route('/receive_heart_rate_data/<patient_id>', methods=['POST'])(self.receive_heart_rate_data)
        self.app.route('/edit_patient/<patient_id>', methods=['GET', 'POST'])(self.edit_patient)
        self.app.route('/patient_monitor/<patient_id>', methods=['GET', 'POST'])(self.patient_monitor)

    def index(self):
        return render_template('index.html')

    def register_doctor(self):
        if request.method == 'POST':
            doctor_id = request.form['doctor_id']
            doctor_password = request.form['doctor_password']
            self.doctors_collection.insert_one({'_id': doctor_id, 'password': doctor_password})
            return redirect(url_for('index'))
        return render_template('register_doctor.html')

    def register_patient(self):
        if request.method == 'POST':
            doctor_id = request.form['doctor_id']
            patient_name = request.form['patient_name']
            patient_password = request.form['patient_password']
            date_of_birth = request.form['date_of_birth']
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
            return render_template('registration_success.html', patient=patient)
        return render_template('register_patient.html')

    def login(self):
        user_type = request.form.get('type')
        user_id = request.form.get('user_id')
        user_password = request.form.get('user_password')

        if user_type == 'doctor':
            doctor = self.doctors_collection.find_one({'_id': user_id, 'password': user_password})
            if doctor:
                return redirect(url_for('doctor_dashboard', doctor_id=user_id))
        elif user_type == 'patient':
            patient = self.patients_collection.find_one({'_id': user_id, 'password': user_password})
            if patient:
                return redirect(url_for('patient_dashboard', patient_id=user_id))
        return redirect(url_for('index'))

    def doctor_login(self):
        return render_template('doctor_login.html')

    def doctor_dashboard(self):
        current_doctor_id = request.args.get('doctor_id')
        patients = list(self.patients_collection.find({'doctor_id': current_doctor_id}))
        return render_template('doctor_dashboard.html', patients=patients, doctor_id=current_doctor_id)

    def receive_temperature_data(self, patient_id):
        data = request.json
        if patient_id:
            data['timestamp'] = datetime.now().isoformat()
            self.temperature_collection.insert_one({'patient_id': patient_id, 'data': data})
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Patient ID not provided'})

    def receive_heart_rate_data(self, patient_id):
        data = request.json
        if patient_id:
            data['timestamp'] = datetime.now().isoformat()
            self.heart_rate_collection.insert_one({'patient_id': patient_id, 'data': data})
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Patient ID not provided'})

    def edit_patient(self, patient_id):
        current_doctor_id = request.args.get('doctor_id')
        if request.method == 'POST':
            return redirect(url_for('doctor_dashboard', doctor_id=current_doctor_id))
        else:
            patient = self.patients_collection.find_one({'_id': patient_id})
            return render_template('edit_patient.html', patient=patient, doctor_id=current_doctor_id)

    def patient_monitor(self, patient_id):
        temperature_data = list(self.temperature_collection.find({'patient_id': patient_id}))
        heart_rate_data = list(self.heart_rate_collection.find({'patient_id': patient_id}))

        if not temperature_data and not heart_rate_data:
            return 'No data found for this patient'

        temperature_values = []
        heart_rate_values = []
        timestamps_temperature = []
        timestamps_heart_rate = []

        for temp_data in temperature_data:
            temperature_values.append(temp_data['data']['temperature'])
            timestamps_temperature.append(temp_data['data']['timestamp'])

        for hr_data in heart_rate_data:
            heart_rate_values.append(hr_data['data']['heart_rate'])
            timestamps_heart_rate.append(hr_data['data']['timestamp'])

        temperature_fig = go.Figure(
            data=go.Scatter(x=timestamps_temperature, y=temperature_values, mode='lines', name='Temperature'))
        heart_rate_fig = go.Figure(
            data=go.Scatter(x=timestamps_heart_rate, y=heart_rate_values, mode='lines', name='Heart Rate'))

        temperature_graph = temperature_fig.to_html(full_html=False)
        heart_rate_graph = heart_rate_fig.to_html(full_html=False)

        avg_temperature = round(sum(temperature_values) / len(temperature_values), 1) if temperature_values else None
        avg_heart_rate = round(sum(heart_rate_values) / len(heart_rate_values), 1) if heart_rate_values else None

        return render_template('patient_monitor.html', patient_id=patient_id, temperature_graph=temperature_graph,
                               heart_rate_graph=heart_rate_graph, avg_temperature=avg_temperature,
                               avg_heart_rate=avg_heart_rate)


if __name__ == '__main__':
    app = Flask(__name__)
    web_app = WebApp(app)
    app.run(debug=True)
