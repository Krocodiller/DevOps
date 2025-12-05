import pytest
from app import app, redis_client

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Простой тест главной страницы."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Медицинский Кооператив' in response.data

def test_redis_works():
    """Простой тест Redis."""
    redis_client.set('test', '123')
    value = redis_client.get('test')
    assert value == '123'

def test_login_page_exists(client):
    """Тест что страница логина доступна."""
    response = client.get('/login')
    assert response.status_code == 200

def test_visit_counter_increments(client):
    """Тест что счетчик посещений увеличивается."""
    visits_before = int(redis_client.get('page_visits') or 0)
    client.get('/')
    visits_after = int(redis_client.get('page_visits') or 0)
    assert visits_after == visits_before + 1
