from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class TestUserLogin(TestCase):

    def setUp(self):
        """
        Set up a test users and client instance.
        """
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='password')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()

    def test_user_login_status(self):
        """
        Test user login status.

        Log in a user and verify that they are authenticated when accessing a protected view.
        """
        # Log the user in
        self.client.login(username='testuser', password='password')

        # Make a request to a view that requires login
        response = self.client.get('/social/event/')

        # Assert that the user is logged in (status code 200 indicates success)
        self.assertEqual(response.status_code, 200)

        # You can also assert the user's state directly
        user = response.context['user']
        self.assertTrue(user.is_authenticated)

    def test_user_logout_status(self):
        """
        Test user logout status.

        Log out a previously logged in user and verify that they are no longer authenticated.
        """
        # Log the user in first
        self.client.login(username='testuser', password='password')

        # Now log them out
        self.client.logout()

        # Make a request to a view that should be accessible to logged out users
        response = self.client.get('/')

        # Assert that the user is logged out (status code 200 indicates success)
        self.assertEqual(response.status_code, 200)

        # You can also assert the user's state directly
        user = response.context.get('user')
        self.assertFalse(user.is_authenticated)
    
    def test_admin_login_acces_admin_panel(self):
        # Login the admin user
        self.client.force_login(self.admin_user)

        # Test access to the Django admin panel
        response = self.client.get('/admin/')
        
        # Assert that the admin user has access (status code 200 indicates success)
        self.assertEqual(response.status_code, 200)
    
    def test_admin_can_create_user(self):
        # Login the admin user
        self.client.force_login(self.admin_user)

        # Test if the admin user can create a new user through the admin interface
        create_user_url = reverse('admin:auth_user_add')
        response = self.client.get(create_user_url)
        
        # Assert that the admin user has access to the create user page (status code 200)
        self.assertEqual(response.status_code, 200)
    
    def test_admin_logout(self):
        # Log the admin in first
        self.client.login(username='adminuser', password='password')

        # Now log them out
        self.client.logout()

        # Make a request to a view that should be accessible to logged out users
        response = self.client.get('/admin/')

        # Assert that the user is logged out (status code 200 indicates success)
        self.assertNotEqual(response.status_code, 200)




