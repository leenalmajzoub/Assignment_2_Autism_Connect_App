from django.contrib.auth.models import User
from django.utils import timezone
from social.models import Event
from .fixtures import client
import pytest

# Add Users

@pytest.fixture
def user1():
    user = User.objects.create(username='testuser1', password='testpassword1')
    return user

@pytest.fixture
def user2():
    user = User.objects.create(username='testuser2', password='testpassword2')

    return user

@pytest.fixture
def logged_in_client1(client, user1):
    client.force_login(user1)
    return client

# Add Events
@pytest.fixture
def event1(user1):
    event1 = Event.objects.create(
            title='Test Event 1',
            description='This is a test event',
            start_time=timezone.now(),
            end_time=timezone.now(),
            organizer=user1,
            attendees_allowed=10,
            place='Test Place 1'
        )
    
    return event1