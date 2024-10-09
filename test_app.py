import pytest
import tempfile
import os
import json
import io  # Import io for using BytesIO
from app import app, init_db


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.app_context():
        init_db()
        yield app.test_client()

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_index_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/get_started' in response.location


def test_get_started(client):
    response = client.get('/get_started')
    assert response.status_code == 200
    assert b'Get Started' in response.data


def test_home(client):
    # Simulate a logged-in user by setting the session
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
    response = client.get('/home')
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    print("Response data:", response.data.decode('utf-8'))
    assert b'Welcome to the Home Page' in response.data, "Expected content not found in the response"

# Test for unauthenticated access to home route
def test_home_unauthenticated(client):
    response = client.get('/home', follow_redirects=True)

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert b'You need to log in first!' in response.data, "Expected flash message not found in the response"
    assert b'Login' in response.data, "Not redirected to login page as expected"
    print("Unauthenticated home route test passed successfully!")
    assert response.status_code == 200




def test_upload(client):
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'Upload' in response.data


def test_classify_get(client):
    response = client.get('/classify')
    assert response.status_code == 200
    assert b'Classify' in response.data


def test_classify_post_invalid_file(client):
    data = {'file': (io.BytesIO(b"abcdef"), 'test.txt')}
    response = client.post('/classify', data=data, content_type='multipart/form-data')
    assert response.status_code == 302  # Redirect


def test_activities(client):
    response = client.get('/activities')
    assert response.status_code == 200
    assert b'Activities' in response.data


def test_clear_table(client):
    response = client.post('/clear_table')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'All records deleted successfully.'


def test_weather(client):
    response = client.get('/weather')
    assert response.status_code == 200
    assert b'Weather' in response.data


def test_learning(client):
    response = client.get('/learning')
    assert response.status_code == 200
    assert b'Learning' in response.data


def test_news(client):
    response = client.get('/news')
    assert response.status_code == 200
    assert b'News' in response.data


def test_analytics(client):
    response = client.get('/analytics')
    assert response.status_code == 200
    assert b'Analytics' in response.data


def test_help(client):
    response = client.get('/help')
    assert response.status_code == 200
    assert b'Help' in response.data


def test_about(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About' in response.data


def test_settings(client):
    # First, simulate a login
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'  # Add user to session

    # Now try to access the settings page
    response = client.get('/settings')
    
    # Check status code
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    
    # Check if 'Settings' is in the response data
    assert b'Settings' in response.data, "The word 'Settings' was not found in the response"
    
    # Check if the username is in the response data
    assert b'testuser' in response.data, "The username 'testuser' was not found in the response"
    
    # Additional checks
    assert b'<title>Settings</title>' in response.data, "The title 'Settings' was not found in the response"
    assert b'<h1>Settings</h1>' in response.data, "The h1 'Settings' was not found in the response"

    print("All assertions passed successfully!")

    # Optionally, print the response data for debugging
    print(response.data.decode('utf-8'))


def test_app_intro(client):
    response = client.get('/intro')
    assert response.status_code == 200
    assert b'AgriTech Innovators' in response.data


if __name__ == '__main__':
    pytest.main()
