"""
Утилиты для медицинского приложения
"""

from datetime import date, datetime
from app import db, Patient, Doctor, Medicine, Visit, Prescription

def get_statistics():
    """Получение общей статистики системы"""
    stats = {
        'total_patients': Patient.query.count(),
        'total_doctors': Doctor.query.count(),
        'total_medicines': Medicine.query.count(),
        'total_visits': Visit.query.count(),
        'visits_today': Visit.query.filter_by(date=date.today()).count(),
        'visits_this_week': Visit.query.filter(
            Visit.date >= date.today().replace(day=date.today().day-7)
        ).count()
    }
    return stats

def get_popular_diagnoses(limit=5):
    """Получение самых частых диагнозов"""
    from sqlalchemy import func
    
    popular = db.session.query(
        Visit.diagnosis,
        func.count(Visit.diagnosis).label('count')
    ).group_by(Visit.diagnosis).order_by(
        func.count(Visit.diagnosis).desc()
    ).limit(limit).all()
    
    return [{'diagnosis': d[0], 'count': d[1]} for d in popular]

def get_popular_medicines(limit=5):
    """Получение самых назначаемых лекарств"""
    from sqlalchemy import func
    
    popular = db.session.query(
        Medicine.name,
        func.count(Prescription.medicine_id).label('count')
    ).join(Prescription).group_by(Medicine.name).order_by(
        func.count(Prescription.medicine_id).desc()
    ).limit(limit).all()
    
    return [{'medicine': m[0], 'count': m[1]} for m in popular]

def search_patients(query):
    """Поиск пациентов по имени или адресу"""
    return Patient.query.filter(
        (Patient.name.contains(query)) |
        (Patient.address.contains(query))
    ).all()

def get_patient_history(patient_id):
    """Получение истории визитов пациента"""
    return Visit.query.filter_by(patient_id=patient_id).order_by(Visit.date.desc()).all()

def get_doctor_schedule(doctor_id, start_date, end_date):
    """Получение расписания врача за период"""
    return Visit.query.filter(
        Visit.doctor_id == doctor_id,
        Visit.date >= start_date,
        Visit.date <= end_date
    ).order_by(Visit.date).all()

def export_visits_to_csv(start_date, end_date):
    """Экспорт визитов в CSV формат"""
    import csv
    import io
    
    visits = Visit.query.filter(
        Visit.date >= start_date,
        Visit.date <= end_date
    ).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow([
        'Дата', 'Пациент', 'Врач', 'Место', 'Симптомы', 
        'Диагноз', 'Предписания', 'Лекарства'
    ])
    
    # Данные
    for visit in visits:
        medicines = ', '.join([p.medicine.name for p in visit.prescriptions])
        writer.writerow([
            visit.date.strftime('%Y-%m-%d'),
            visit.patient.name,
            visit.doctor.name,
            visit.location,
            visit.symptoms,
            visit.diagnosis,
            visit.prescriptions_text,
            medicines
        ])
    
    return output.getvalue()

def validate_patient_data(data):
    """Валидация данных пациента"""
    errors = []
    
    if not data.get('name') or len(data['name'].strip()) < 2:
        errors.append('Имя должно содержать минимум 2 символа')
    
    if data.get('gender') not in ['Мужской', 'Женский']:
        errors.append('Пол должен быть "Мужской" или "Женский"')
    
    if not data.get('birth_date'):
        errors.append('Дата рождения обязательна')
    else:
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            if birth_date > date.today():
                errors.append('Дата рождения не может быть в будущем')
        except ValueError:
            errors.append('Неверный формат даты рождения')
    
    if not data.get('address') or len(data['address'].strip()) < 5:
        errors.append('Адрес должен содержать минимум 5 символов')
    
    return errors

def validate_medicine_data(data):
    """Валидация данных лекарства"""
    errors = []
    
    if not data.get('name') or len(data['name'].strip()) < 2:
        errors.append('Название лекарства должно содержать минимум 2 символа')
    
    if not data.get('usage_method') or len(data['usage_method'].strip()) < 5:
        errors.append('Способ приема должен содержать минимум 5 символов')
    
    if not data.get('description') or len(data['description'].strip()) < 10:
        errors.append('Описание должно содержать минимум 10 символов')
    
    if not data.get('side_effects') or len(data['side_effects'].strip()) < 5:
        errors.append('Описание побочных эффектов должно содержать минимум 5 символов')
    
    return errors
