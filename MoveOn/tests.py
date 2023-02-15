import pytest
from django.urls import reverse
from django.test import Client
from MoveOn.models import *
from django.contrib.auth.models import User


@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_create_user_view(client):
    url = reverse('create_user')
    response = client.get(url)

    assert response.status_code == 200

@pytest.mark.django_db
def test_logout_view(client):
    #log in
    client.login(username='username', password='password')
    #logout view
    response = client.get(reverse('logout'))
    #correctly redirect
    assert response.status_code == 302
    assert response.url == '/'
    #is user logged out
    user = response.wsgi_request.user
    assert user.is_authenticated == False


@pytest.mark.django_db
def test_login_view(client):
    #Create User
    User.objects.create_user(
        username='test_user', password='test_password')

    #Go to log in page
    url = reverse('login')
    response = client.get(url)

    #Check if is loaded correctly
    assert response.status_code == 200

    # Send form
    response = client.post(url, {'username': 'test_user', 'password': 'test_password'})

    #Check if is loaded correctly
    assert response.status_code == 302
    assert response.url == '/creating_details/1/'
    assert client.login(username='test_user', password='test_password')

    #Form with wrong data
    response = client.post(url, {'username': 'test_user', 'password': 'wrong_password'})

    #Check if is not logged in
    assert response.status_code == 302
    assert response.url == '/login/'
    assert not client.login(username='test_user', password='wrong_password')

@pytest.mark.django_db
def test_create_user_view_with_valid_data(client):
    url = reverse('create_user')
    data = {
        'login': 'testuser',
        'password': 'mareczek',
        'password2': 'mareczek',
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'account_type': '1',
    }

    response = client.post(url, data, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == [(reverse('details', args=[2]), 302)]


@pytest.mark.django_db
def test_create_user_view_with_invalid_data(client):
    url = reverse('create_user')
    data = {
        'login': 'testuser',
        'password': 'testpass',
        'password2': 'testpass',
        'email': 'invalidemail',  # invalid email format
        'first_name': 'Test',
        'last_name': 'User',
        'account_type': '1',
    }

    response = client.post(url, data, follow=True)


    assert response.status_code == 200
    assert response.redirect_chain == [(reverse('create_user'), 302)]


@pytest.mark.django_db
def test_pupil_details_view(client):
    user = User.objects.create_user(
        username='test',
        password='testuser',
        email='testuser@example.com',
        first_name='Test',
        last_name='User',
    )

    client.login(username='test', password='testuser')
    url = reverse('details', args=[user.id])
    response = client.get(url)

    assert response.status_code == 200

    trainer = Trainer.objects.create(user=user, first_name='Trainer', last_name='Test')
    data = {
        'name': 'Test',
        'last_name': 'User',
        'starting_weight': '80',
        'height': '190',
        'trainer': trainer.id,
    }

    response = client.post(url, data, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == [(reverse('main_pupil', args=[1]), 302)]

