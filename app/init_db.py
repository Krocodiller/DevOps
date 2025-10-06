#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных с тестовыми данными
"""

from app import app, db, User, Patient, Doctor, Medicine, Visit, Prescription
from datetime import date, datetime
from werkzeug.security import generate_password_hash

def init_database():
    """Инициализация базы данных с тестовыми данными"""
    
    with app.app_context():
        # Очистка существующих данных
        db.drop_all()
        db.create_all()
        
        print("Создание тестовых данных...")
        
        # Создание пользователей
        users_data = [
            {
                'username': 'admin',
                'password_hash': generate_password_hash('admin123'),
                'role': 'admin',
                'name': 'Администратор Системы',
                'is_active': True
            },
            {
                'username': 'doctor',
                'password_hash': generate_password_hash('doctor123'),
                'role': 'doctor',
                'name': 'Доктор Иванов',
                'is_active': True
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(**user_data)
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print("Пользователи созданы")
        
        # Создание пациентов
        patients_data = [
            {
                'name': 'Иванов Иван Иванович',
                'gender': 'Мужской',
                'birth_date': date(1985, 5, 15),
                'address': 'г. Москва, ул. Ленина, д. 10, кв. 5'
            },
            {
                'name': 'Петрова Анна Сергеевна',
                'gender': 'Женский',
                'birth_date': date(1990, 8, 22),
                'address': 'г. Москва, ул. Пушкина, д. 25, кв. 12'
            },
            {
                'name': 'Сидоров Петр Александрович',
                'gender': 'Мужской',
                'birth_date': date(1978, 12, 3),
                'address': 'г. Москва, ул. Гагарина, д. 7, кв. 8'
            },
            {
                'name': 'Козлова Мария Владимировна',
                'gender': 'Женский',
                'birth_date': date(1995, 3, 18),
                'address': 'г. Москва, ул. Мира, д. 15, кв. 3'
            }
        ]
        
        patients = []
        for patient_data in patients_data:
            patient = Patient(**patient_data)
            db.session.add(patient)
            patients.append(patient)
        
        # Создание врачей
        doctors_data = [
            {'name': 'Смирнов Алексей Петрович'},
            {'name': 'Волкова Елена Михайловна'},
            {'name': 'Новиков Дмитрий Сергеевич'}
        ]
        
        doctors = []
        for doctor_data in doctors_data:
            doctor = Doctor(**doctor_data)
            db.session.add(doctor)
            doctors.append(doctor)
        
        # Создание лекарств
        medicines_data = [
            {
                'name': 'Парацетамол',
                'usage_method': 'По 1 таблетке 3 раза в день после еды',
                'description': 'Жаропонижающее и обезболивающее средство',
                'side_effects': 'Возможны аллергические реакции, тошнота, боли в животе'
            },
            {
                'name': 'Амоксициллин',
                'usage_method': 'По 500 мг 3 раза в день в течение 7 дней',
                'description': 'Антибактериальный препарат широкого спектра действия',
                'side_effects': 'Диарея, тошнота, рвота, аллергические реакции'
            },
            {
                'name': 'Ибупрофен',
                'usage_method': 'По 200-400 мг 3-4 раза в день',
                'description': 'Противовоспалительное, жаропонижающее и обезболивающее средство',
                'side_effects': 'Изжога, тошнота, головная боль, головокружение'
            },
            {
                'name': 'Лоратадин',
                'usage_method': 'По 1 таблетке 1 раз в день',
                'description': 'Антигистаминный препарат для лечения аллергии',
                'side_effects': 'Сонливость, сухость во рту, головная боль'
            }
        ]
        
        medicines = []
        for medicine_data in medicines_data:
            medicine = Medicine(**medicine_data)
            db.session.add(medicine)
            medicines.append(medicine)
        
        db.session.commit()
        print("Пациенты, врачи и лекарства созданы")
        
        # Создание визитов
        visits_data = [
            {
                'date': date(2024, 1, 15),
                'location': 'Поликлиника №1, кабинет 205',
                'symptoms': 'Повышенная температура, кашель, насморк',
                'diagnosis': 'ОРВИ',
                'prescriptions_text': 'Постельный режим, обильное питье, симптоматическое лечение',
                'patient_id': patients[0].id,
                'doctor_id': doctors[0].id,
                'medicine_ids': [medicines[0].id, medicines[2].id]
            },
            {
                'date': date(2024, 1, 15),
                'location': 'Поликлиника №1, кабинет 210',
                'symptoms': 'Боль в горле, затрудненное глотание',
                'diagnosis': 'Ангина',
                'prescriptions_text': 'Антибактериальная терапия, полоскание горла',
                'patient_id': patients[1].id,
                'doctor_id': doctors[1].id,
                'medicine_ids': [medicines[1].id]
            },
            {
                'date': date(2024, 1, 16),
                'location': 'Домашний визит',
                'symptoms': 'Сыпь на коже, зуд',
                'diagnosis': 'Аллергическая реакция',
                'prescriptions_text': 'Исключить аллерген, антигистаминная терапия',
                'patient_id': patients[2].id,
                'doctor_id': doctors[2].id,
                'medicine_ids': [medicines[3].id]
            },
            {
                'date': date(2024, 1, 16),
                'location': 'Поликлиника №1, кабинет 205',
                'symptoms': 'Головная боль, слабость',
                'diagnosis': 'Головная боль напряжения',
                'prescriptions_text': 'Обезболивающая терапия, отдых',
                'patient_id': patients[3].id,
                'doctor_id': doctors[0].id,
                'medicine_ids': [medicines[2].id]
            },
            {
                'date': date(2024, 1, 17),
                'location': 'Поликлиника №1, кабинет 210',
                'symptoms': 'Кашель с мокротой, одышка',
                'diagnosis': 'Бронхит',
                'prescriptions_text': 'Антибактериальная терапия, отхаркивающие средства',
                'patient_id': patients[0].id,
                'doctor_id': doctors[1].id,
                'medicine_ids': [medicines[1].id, medicines[0].id]
            }
        ]
        
        for visit_data in visits_data:
            medicine_ids = visit_data.pop('medicine_ids')
            visit = Visit(**visit_data)
            db.session.add(visit)
            db.session.flush()  # Получаем ID визита
            
            # Добавляем рецепты
            for medicine_id in medicine_ids:
                prescription = Prescription(
                    visit_id=visit.id,
                    medicine_id=medicine_id
                )
                db.session.add(prescription)
        
        db.session.commit()
        print("Визиты и рецепты созданы")
        
        print("\n=== ТЕСТОВЫЕ ДАННЫЕ СОЗДАНЫ ===")
        print(f"Пользователей: {len(users)}")
        print(f"Пациентов: {len(patients)}")
        print(f"Врачей: {len(doctors)}")
        print(f"Лекарств: {len(medicines)}")
        print(f"Визитов: {len(visits_data)}")
        print("\n=== ТЕСТОВЫЕ АККАУНТЫ ===")
        print("Администратор:")
        print("  Логин: admin")
        print("  Пароль: admin123")
        print("  Права: Полный доступ")
        print("\nВрач:")
        print("  Логин: doctor")
        print("  Пароль: doctor123")
        print("  Права: Пациенты, визиты, лекарства")
        print("\nДля запуска приложения выполните: python app.py")

if __name__ == '__main__':
    init_database()
