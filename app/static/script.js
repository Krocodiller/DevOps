// JavaScript для медицинского приложения

// Глобальные переменные
let patients = [];
let doctors = [];
let medicines = [];
let visits = [];

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    loadAllData();
    setupEventListeners();
    setTodayDate();
    checkUserRole();
});

// Установка сегодняшней даты в поля даты
function setTodayDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('visitDate').value = today;
    document.getElementById('analyticsDate').value = today;
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Формы
    document.getElementById('patientForm').addEventListener('submit', handlePatientSubmit);
    document.getElementById('doctorForm').addEventListener('submit', handleDoctorSubmit);
    document.getElementById('medicineForm').addEventListener('submit', handleMedicineSubmit);
    document.getElementById('visitForm').addEventListener('submit', handleVisitSubmit);
    
    // Аналитика
    document.getElementById('visitsByDateForm').addEventListener('submit', handleVisitsByDate);
    document.getElementById('patientsByDiagnosisForm').addEventListener('submit', handlePatientsByDiagnosis);
    document.getElementById('medicineSideEffectsForm').addEventListener('submit', handleMedicineSideEffects);
}

// Загрузка всех данных
async function loadAllData() {
    try {
        const promises = [loadPatients(), loadMedicines(), loadVisits()];
        
        // Загружаем врачей только для администраторов
        const userRole = document.querySelector('.user-role');
        if (userRole && userRole.textContent === 'Администратор') {
            promises.push(loadDoctors());
        }
        
        await Promise.all(promises);
        updateSelectOptions();
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        if (error.message.includes('401') || error.message.includes('403')) {
            showAlert('Сессия истекла. Пожалуйста, войдите в систему заново.', 'danger');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            showAlert('Ошибка загрузки данных', 'danger');
        }
    }
}

// Загрузка пациентов
async function loadPatients() {
    try {
        const response = await fetch('/api/patients');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        patients = await response.json();
        displayPatients();
    } catch (error) {
        console.error('Ошибка загрузки пациентов:', error);
        throw error;
    }
}

// Загрузка врачей
async function loadDoctors() {
    try {
        const response = await fetch('/api/doctors');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        doctors = await response.json();
        displayDoctors();
    } catch (error) {
        console.error('Ошибка загрузки врачей:', error);
        throw error;
    }
}

// Загрузка лекарств
async function loadMedicines() {
    try {
        const response = await fetch('/api/medicines');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        medicines = await response.json();
        displayMedicines();
    } catch (error) {
        console.error('Ошибка загрузки лекарств:', error);
        throw error;
    }
}

// Загрузка визитов
async function loadVisits() {
    try {
        const response = await fetch('/api/visits');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        visits = await response.json();
        displayVisits();
    } catch (error) {
        console.error('Ошибка загрузки визитов:', error);
        throw error;
    }
}

// Отображение пациентов
function displayPatients() {
    const container = document.getElementById('patientsList');
    if (patients.length === 0) {
        container.innerHTML = '<p>Пациенты не найдены</p>';
        return;
    }

    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Имя</th>
                    <th>Пол</th>
                    <th>Дата рождения</th>
                    <th>Адрес</th>
                </tr>
            </thead>
            <tbody>
                ${patients.map(patient => `
                    <tr>
                        <td>${patient.name}</td>
                        <td>${patient.gender}</td>
                        <td>${formatDate(patient.birth_date)}</td>
                        <td class="long-text">${patient.address}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = html;
}

// Отображение врачей
function displayDoctors() {
    const container = document.getElementById('doctorsList');
    if (doctors.length === 0) {
        container.innerHTML = '<p>Врачи не найдены</p>';
        return;
    }

    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Имя врача</th>
                </tr>
            </thead>
            <tbody>
                ${doctors.map(doctor => `
                    <tr>
                        <td>${doctor.name}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = html;
}

// Отображение лекарств
function displayMedicines() {
    const container = document.getElementById('medicinesList');
    if (medicines.length === 0) {
        container.innerHTML = '<p>Лекарства не найдены</p>';
        return;
    }

    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Название</th>
                    <th>Способ приема</th>
                    <th>Описание</th>
                    <th>Побочные эффекты</th>
                </tr>
            </thead>
            <tbody>
                ${medicines.map(medicine => `
                    <tr>
                        <td><strong>${medicine.name}</strong></td>
                        <td class="long-text">${medicine.usage_method}</td>
                        <td class="long-text">${medicine.description}</td>
                        <td class="long-text">${medicine.side_effects}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = html;
}

// Отображение визитов
function displayVisits() {
    const container = document.getElementById('visitsList');
    if (visits.length === 0) {
        container.innerHTML = '<p>Визиты не найдены</p>';
        return;
    }

    const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Дата</th>
                    <th>Пациент</th>
                    <th>Врач</th>
                    <th>Место</th>
                    <th>Диагноз</th>
                    <th>Лекарства</th>
                </tr>
            </thead>
            <tbody>
                ${visits.map(visit => `
                    <tr>
                        <td>${formatDate(visit.date)}</td>
                        <td>${visit.patient_name}</td>
                        <td>${visit.doctor_name}</td>
                        <td class="long-text">${visit.location}</td>
                        <td>${visit.diagnosis}</td>
                        <td class="long-text">${visit.medicines.join(', ') || 'Не назначены'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = html;
}

// Обновление опций в селектах
function updateSelectOptions() {
    // Пациенты
    const patientSelect = document.getElementById('visitPatient');
    patientSelect.innerHTML = '<option value="">Выберите пациента</option>' +
        patients.map(p => `<option value="${p.id}">${p.name}</option>`).join('');

    // Врачи
    const doctorSelect = document.getElementById('visitDoctor');
    doctorSelect.innerHTML = '<option value="">Выберите врача</option>' +
        doctors.map(d => `<option value="${d.id}">${d.name}</option>`).join('');

    // Лекарства для визита
    const medicineSelect = document.getElementById('visitMedicines');
    medicineSelect.innerHTML = medicines.map(m => `<option value="${m.id}">${m.name}</option>`).join('');

    // Лекарства для аналитики
    const analyticsMedicineSelect = document.getElementById('analyticsMedicine');
    analyticsMedicineSelect.innerHTML = '<option value="">Выберите лекарство</option>' +
        medicines.map(m => `<option value="${m.id}">${m.name}</option>`).join('');
}

// Обработка добавления пациента
async function handlePatientSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('patientName').value,
        gender: document.getElementById('patientGender').value,
        birth_date: document.getElementById('patientBirthDate').value,
        address: document.getElementById('patientAddress').value
    };

    try {
        const response = await fetch('/api/patients', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showAlert('Пациент успешно добавлен!', 'success');
            document.getElementById('patientForm').reset();
            loadPatients();
            updateSelectOptions();
        } else {
            throw new Error('Ошибка добавления пациента');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showAlert('Ошибка добавления пациента', 'danger');
    }
}

// Обработка добавления врача
async function handleDoctorSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('doctorName').value
    };

    try {
        const response = await fetch('/api/doctors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showAlert('Врач успешно добавлен!', 'success');
            document.getElementById('doctorForm').reset();
            loadDoctors();
            updateSelectOptions();
        } else {
            throw new Error('Ошибка добавления врача');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showAlert('Ошибка добавления врача', 'danger');
    }
}

// Обработка добавления лекарства
async function handleMedicineSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('medicineName').value,
        usage_method: document.getElementById('medicineUsage').value,
        description: document.getElementById('medicineDescription').value,
        side_effects: document.getElementById('medicineSideEffects').value
    };

    try {
        const response = await fetch('/api/medicines', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showAlert('Лекарство успешно добавлено!', 'success');
            document.getElementById('medicineForm').reset();
            loadMedicines();
            updateSelectOptions();
        } else {
            throw new Error('Ошибка добавления лекарства');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showAlert('Ошибка добавления лекарства', 'danger');
    }
}

// Обработка добавления визита
async function handleVisitSubmit(e) {
    e.preventDefault();
    
    const selectedMedicines = Array.from(document.getElementById('visitMedicines').selectedOptions)
        .map(option => parseInt(option.value));

    const formData = {
        date: document.getElementById('visitDate').value,
        location: document.getElementById('visitLocation').value,
        patient_id: parseInt(document.getElementById('visitPatient').value),
        doctor_id: parseInt(document.getElementById('visitDoctor').value),
        symptoms: document.getElementById('visitSymptoms').value,
        diagnosis: document.getElementById('visitDiagnosis').value,
        prescriptions_text: document.getElementById('visitPrescriptions').value,
        medicine_ids: selectedMedicines
    };

    try {
        const response = await fetch('/api/visits', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            showAlert('Визит успешно записан!', 'success');
            document.getElementById('visitForm').reset();
            setTodayDate();
            loadVisits();
        } else {
            throw new Error('Ошибка записи визита');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showAlert('Ошибка записи визита', 'danger');
    }
}

// Аналитика: количество вызовов по дате
async function handleVisitsByDate(e) {
    e.preventDefault();
    
    const date = document.getElementById('analyticsDate').value;
    
    try {
        const response = await fetch('/api/visits/count-by-date', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ date })
        });

        const result = await response.json();
        document.getElementById('visitsCount').textContent = result.count;
        document.getElementById('visitsByDateResult').style.display = 'block';
    } catch (error) {
        console.error('Ошибка:', error);
        showAlert('Ошибка получения данных', 'danger');
    }
}

// Аналитика: количество больных по болезни
async function handlePatientsByDiagnosis(e) {
    e.preventDefault();
    
    const diagnosis = document.getElementById('analyticsDiagnosis').value;
    
    try {
        const response = await fetch('/api/patients/count-by-diagnosis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ diagnosis })
        });

        const result = await response.json();
        document.getElementById('patientsCount').textContent = result.count;
        document.getElementById('patientsByDiagnosisResult').style.display = 'block';
    } catch (error) {
        console.error('Ошибка:', error);
        showAlert('Ошибка получения данных', 'danger');
    }
}

// Аналитика: побочные эффекты лекарства
async function handleMedicineSideEffects(e) {
    e.preventDefault();
    
    const medicineId = document.getElementById('analyticsMedicine').value;
    
    try {
        const response = await fetch(`/api/medicines/${medicineId}/side-effects`);
        const result = await response.json();
        
        document.getElementById('medicineNameResult').textContent = result.name;
        document.getElementById('medicineSideEffectsText').textContent = result.side_effects;
        document.getElementById('medicineSideEffectsResult').style.display = 'block';
    } catch (error) {
        console.error('Ошибка:', error);
        showAlert('Ошибка получения данных', 'danger');
    }
}

// Проверка роли пользователя
function checkUserRole() {
    // Проверяем, есть ли элемент с информацией о пользователе
    const userInfo = document.querySelector('.user-info');
    if (!userInfo) {
        // Если нет информации о пользователе, перенаправляем на страницу входа
        window.location.href = '/login';
        return;
    }
    
    // Скрываем вкладку врачей для обычных врачей
    const userRole = document.querySelector('.user-role').textContent;
    if (userRole === 'Врач') {
        const doctorsTab = document.querySelector('button[onclick="showTab(\'doctors\')"]');
        if (doctorsTab) {
            doctorsTab.style.display = 'none';
        }
    }
}

// Переключение вкладок
function showTab(tabName) {
    // Проверяем права доступа
    const userRole = document.querySelector('.user-role');
    if (userRole && userRole.textContent === 'Врач' && tabName === 'doctors') {
        showAlert('У вас нет прав для доступа к управлению врачами', 'danger');
        return;
    }
    
    // Скрыть все вкладки
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Убрать активный класс с кнопок
    const buttons = document.querySelectorAll('.nav-tab');
    buttons.forEach(button => button.classList.remove('active'));
    
    // Показать выбранную вкладку
    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Добавить активный класс к кнопке
    event.target.classList.add('active');
    
    // Загрузить данные при переключении на аналитику
    if (tabName === 'analytics') {
        loadMedicines(); // Обновить список лекарств для аналитики
        loadStatistics();
        loadPopularDiagnoses();
        loadPopularMedicines();
    }
}

// Показать уведомление
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Удалить уведомление через 5 секунд
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

// Загрузка статистики
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();
        
        const container = document.getElementById('statistics');
        container.innerHTML = `
            <div class="result-box">
                <div class="result-number">${stats.total_patients}</div>
                <div class="result-text">пациентов</div>
            </div>
            <div class="result-box">
                <div class="result-number">${stats.total_doctors}</div>
                <div class="result-text">врачей</div>
            </div>
            <div class="result-box">
                <div class="result-number">${stats.total_medicines}</div>
                <div class="result-text">лекарств</div>
            </div>
            <div class="result-box">
                <div class="result-number">${stats.total_visits}</div>
                <div class="result-text">визитов</div>
            </div>
            <div class="result-box">
                <div class="result-number">${stats.visits_today}</div>
                <div class="result-text">визитов сегодня</div>
            </div>
        `;
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
        document.getElementById('statistics').innerHTML = '<p>Ошибка загрузки статистики</p>';
    }
}

// Загрузка популярных диагнозов
async function loadPopularDiagnoses() {
    try {
        const response = await fetch('/api/popular-diagnoses');
        const diagnoses = await response.json();
        
        const container = document.getElementById('popularDiagnoses');
        if (diagnoses.length === 0) {
            container.innerHTML = '<p>Данные не найдены</p>';
            return;
        }

        const html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Диагноз</th>
                        <th>Количество</th>
                    </tr>
                </thead>
                <tbody>
                    ${diagnoses.map(d => `
                        <tr>
                            <td>${d.diagnosis}</td>
                            <td><strong>${d.count}</strong></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        container.innerHTML = html;
    } catch (error) {
        console.error('Ошибка загрузки диагнозов:', error);
        document.getElementById('popularDiagnoses').innerHTML = '<p>Ошибка загрузки данных</p>';
    }
}

// Загрузка популярных лекарств
async function loadPopularMedicines() {
    try {
        const response = await fetch('/api/popular-medicines');
        const medicines = await response.json();
        
        const container = document.getElementById('popularMedicines');
        if (medicines.length === 0) {
            container.innerHTML = '<p>Данные не найдены</p>';
            return;
        }

        const html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Лекарство</th>
                        <th>Назначений</th>
                    </tr>
                </thead>
                <tbody>
                    ${medicines.map(m => `
                        <tr>
                            <td>${m.medicine}</td>
                            <td><strong>${m.count}</strong></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        container.innerHTML = html;
    } catch (error) {
        console.error('Ошибка загрузки лекарств:', error);
        document.getElementById('popularMedicines').innerHTML = '<p>Ошибка загрузки данных</p>';
    }
}
