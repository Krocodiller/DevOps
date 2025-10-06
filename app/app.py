from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/medical_cooperative.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', 6379)
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

db = SQLAlchemy(app)
CORS(app)

# Модели данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' или 'doctor'
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    visits = db.relationship('Visit', backref='patient', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    visits = db.relationship('Visit', backref='doctor', lazy=True)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    usage_method = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    side_effects = db.Column(db.Text, nullable=False)
    prescriptions = db.relationship('Prescription', backref='medicine', lazy=True)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    prescriptions_text = db.Column(db.Text, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    prescriptions = db.relationship('Prescription', backref='visit', lazy=True)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visit.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)

# Декораторы для аутентификации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Доступ запрещен. Требуются права администратора.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'doctor']:
            flash('Доступ запрещен.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Создание таблиц
with app.app_context():
    db.create_all()
  
# Маршруты аутентификации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            redis_client.incr('successful_logins')
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['name'] = user.name
            flash(f'Добро пожаловать, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            redis_client.incr('failed_logins')
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

# Главная страница со счетчиком посещений
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    # Увеличиваем счетчик посещений
    visit_count = redis_client.incr('page_visits')
    
    # Простая HTML страница для неавторизованных пользователей
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Медицинский Кооператив</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
            }}
            .counter {{ 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px; 
                margin: 20px 0;
                backdrop-filter: blur(10px);
            }}
            .login-btn {{
                background: #fff;
                color: #667eea;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Добро пожаловать в Медицинский Кооператив</h1>
            <div class="counter">
                <h2>Счетчик посещений</h2>
                <p style="font-size: 48px; margin: 20px 0;">{visit_count}</p>
                <p>Это главная страница нашей медицинской системы</p>
            </div>
            <a href="/login" class="login-btn">Войти в систему</a>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template)
# API для пациентов
@app.route('/api/patients', methods=['GET', 'POST'])
@doctor_or_admin_required
def patients():
    if request.method == 'GET':
        patients = Patient.query.all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'gender': p.gender,
            'birth_date': p.birth_date.isoformat(),
            'address': p.address
        } for p in patients])
    
    elif request.method == 'POST':
        data = request.json
        patient = Patient(
            name=data['name'],
            gender=data['gender'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
            address=data['address']
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify({'message': 'Patient added successfully'})

# API для врачей
@app.route('/api/doctors', methods=['GET', 'POST'])
@admin_required
def doctors():
    if request.method == 'GET':
        doctors = Doctor.query.all()
        return jsonify([{
            'id': d.id,
            'name': d.name
        } for d in doctors])
    
    elif request.method == 'POST':
        data = request.json
        doctor = Doctor(name=data['name'])
        db.session.add(doctor)
        db.session.commit()
        return jsonify({'message': 'Doctor added successfully'})

# API для лекарств
@app.route('/api/medicines', methods=['GET', 'POST'])
@doctor_or_admin_required
def medicines():
    if request.method == 'GET':
        medicines = Medicine.query.all()
        return jsonify([{
            'id': m.id,
            'name': m.name,
            'usage_method': m.usage_method,
            'description': m.description,
            'side_effects': m.side_effects
        } for m in medicines])
    
    elif request.method == 'POST':
        data = request.json
        medicine = Medicine(
            name=data['name'],
            usage_method=data['usage_method'],
            description=data['description'],
            side_effects=data['side_effects']
        )
        db.session.add(medicine)
        db.session.commit()
        return jsonify({'message': 'Medicine added successfully'})

# API для визитов
@app.route('/api/visits', methods=['GET', 'POST'])
@doctor_or_admin_required
def visits():
    if request.method == 'GET':
        visits = Visit.query.all()
        return jsonify([{
            'id': v.id,
            'date': v.date.isoformat(),
            'location': v.location,
            'symptoms': v.symptoms,
            'diagnosis': v.diagnosis,
            'prescriptions_text': v.prescriptions_text,
            'patient_name': v.patient.name,
            'doctor_name': v.doctor.name,
            'medicines': [p.medicine.name for p in v.prescriptions]
        } for v in visits])
    
    elif request.method == 'POST':
        data = request.json
        visit = Visit(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            location=data['location'],
            symptoms=data['symptoms'],
            diagnosis=data['diagnosis'],
            prescriptions_text=data['prescriptions_text'],
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id']
        )
        db.session.add(visit)
        db.session.flush()  # Получаем ID визита
        
        # Добавляем рецепты
        for medicine_id in data.get('medicine_ids', []):
            prescription = Prescription(
                visit_id=visit.id,
                medicine_id=medicine_id
            )
            db.session.add(prescription)
        
        db.session.commit()
        return jsonify({'message': 'Visit added successfully'})

# Функционал 1: Количество вызовов по дате
@app.route('/api/visits/count-by-date', methods=['POST'])
@doctor_or_admin_required
def count_visits_by_date():
    data = request.json
    target_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    count = Visit.query.filter_by(date=target_date).count()
    return jsonify({'date': target_date.isoformat(), 'count': count})

# Функционал 2: Количество больных по болезни
@app.route('/api/patients/count-by-diagnosis', methods=['POST'])
@doctor_or_admin_required
def count_patients_by_diagnosis():
    data = request.json
    diagnosis = data['diagnosis']
    count = Visit.query.filter_by(diagnosis=diagnosis).count()
    return jsonify({'diagnosis': diagnosis, 'count': count})

# Функционал 3: Побочные эффекты лекарства
@app.route('/api/medicines/<int:medicine_id>/side-effects')
@doctor_or_admin_required
def get_medicine_side_effects(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    return jsonify({
        'name': medicine.name,
        'side_effects': medicine.side_effects
    })

# Функционал 4: Добавление нового лекарства (уже реализовано в /api/medicines POST)

# Дополнительные API endpoints
@app.route('/api/statistics')
@doctor_or_admin_required
def get_statistics():
    """Получение общей статистики системы"""
    from utils import get_statistics
    return jsonify(get_statistics())

@app.route('/api/popular-diagnoses')
@doctor_or_admin_required
def get_popular_diagnoses():
    """Получение популярных диагнозов"""
    from utils import get_popular_diagnoses
    return jsonify(get_popular_diagnoses())

@app.route('/api/popular-medicines')
@doctor_or_admin_required
def get_popular_medicines():
    """Получение популярных лекарств"""
    from utils import get_popular_medicines
    return jsonify(get_popular_medicines())

@app.route('/api/search-patients')
@doctor_or_admin_required
def search_patients():
    """Поиск пациентов"""
    from utils import search_patients
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    patients = search_patients(query)
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'gender': p.gender,
        'birth_date': p.birth_date.isoformat(),
        'address': p.address
    } for p in patients])

@app.route('/api/patient/<int:patient_id>/history')
@doctor_or_admin_required
def get_patient_history(patient_id):
    """История визитов пациента"""
    from utils import get_patient_history
    visits = get_patient_history(patient_id)
    return jsonify([{
        'id': v.id,
        'date': v.date.isoformat(),
        'location': v.location,
        'symptoms': v.symptoms,
        'diagnosis': v.diagnosis,
        'prescriptions_text': v.prescriptions_text,
        'doctor_name': v.doctor.name,
        'medicines': [p.medicine.name for p in v.prescriptions]
    } for v in visits])

# API для получения статистики посещений
@app.route('/api/visit-stats')
@login_required
def get_visit_stats():
    """Получение статистики посещений страницы"""
    try:
        total_visits = redis_client.get('page_visits') or 0
        return jsonify({
            'total_visits': int(total_visits),
            'message': 'Статистика посещений главной страницы'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)
