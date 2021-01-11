from django.test import TestCase 
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
# CURRENT_URL = reverse('user:current')
ME_URL = reverse('user:me')


def create_user_helper(**params):
    """Helper function to create a user for testing"""

    return get_user_model().objects.create_user(**params)

class PublicUserAPiTests(TestCase):
    """Test the user api public"""

    def setup(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test if user is created successfully"""

        payload = {
            'email': 'test@gmail.com',
            'password': 'test12!@',
            'name': 'test'
        }

        # make a call to create a user
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # check if user is created successfully
        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(payload['password']))

        self.assertNotIn('password', res.data)
    
    def test_already_exist(self):
        """Test create a user that already exist"""

        payload = {
            'email': 'test@gmail.com',
            'password': 'test12!@'
        }

        create_user_helper(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_password_is_short(self):
        """Test if password is less that 5 characters"""

        payload = {
            'email': 'test@gmail.com',
            'password': 'test',
            'name': 'Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(
            email = payload['email']
        ).exists()

        self.assertFalse(user_exist)

    def test_create_token(self):
        """Test that a token is created for a user"""

        payload = {
            'email': 'test@gmail.com',
            'password': 'test12!@'
        }

        create_user_helper(**payload)

        res = self.client.post(TOKEN_URL, payload)

        # check if token is returned in response
        self.assertIn('token', res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_credentials(self):
        """Test if user is providing the invalid credentials"""

        create_user_helper(email='test@gmail.com', password='test12!@')
        payload = {
            'email': 'test@gmail.com',
            'password': 'tes12!@'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Test when you create a token with no user data provided"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test12!@'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_missing_data(self):
        """Test with some feilds are missing"""

        payload = {
            'email': 'test@gmail.com',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_is_required(self): 
        """Test if user is required to login and provide token"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test user Api requests that require user authentication"""

    def setUp(self):
        self.user = create_user_helper(
            email='test@gmail.com',
            password= 'test12!@',
            name='test'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieve profile of a logged in user successfully"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
    
    def test_post_me_not_allowed(self):
        """Test post is not allowed on the ME url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    
    def test_update_user_profile(self):
        """Test updating user profile for authenticated user"""
        payload = {
            'name': 'new name',
            'password': 'new12!@',
            'email': 'new@gmail.com'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    


