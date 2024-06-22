# # conftest.py
# import pytest
# from django.utils import timezone
# from django.contrib.auth.models import User
# from django.test import Client
# from .models import Event

# @pytest.fixture
# def client():
#     return Client()

# @pytest.fixture
# def user(db):
#     return User.objects.create_user(username='testuser', password='testpassword')

# @pytest.fixture
# def logged_in_client(client, user):
#     client.login(username='testuser', password='testpassword')
#     return client

# @pytest.fixture
# def event(db):
#     user = user()
    
#     event = Event.objects.create(
#             title='Test Event',
#             description='This is a test event',
#             start_time=timezone.now(),
#             end_time=timezone.now(),
#             organizer=user,
#             attendees_allowed=10,
#             place='Test Place'
#         )
    
#     return event
