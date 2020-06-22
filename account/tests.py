from django.urls import reverse
from rest_framework import status, exceptions
from rest_framework.test import APITestCase
from .models import User


class UserTests(APITestCase):
    """
    Setup func provides a base user and superuser plus the base urls
    for testing
    """

    def setUp(self):
        self.user_data = {'email': 'user1@test.com',
                          'first_name': 'fuser',
                          'last_name': 'luser',
                          'gender': 'F',
                          'password': 'abcd_1234'}

        self.admin_data = {'email': 'admin1@test.com',
                           'first_name': 'fadmin',
                           'last_name': 'ladmin',
                           'gender': 'M',
                           'password': 'abcd_1234'}

        self.user = User.objects.create_user(**self.user_data)
        self.user = User.objects.create_superuser(**self.admin_data)

        self.create_user_url = reverse('api-create-user')
        self.login_url = reverse('api-login')
        self.change_password_url = reverse('api-change-password')
        self.me_url = reverse('api-me')

        """
        ---- create_user test cases ----
        """
    def test_create_user(self):
        data = self.user_data
        data['email'] = 'user2@test.com'
        data['confirm_password'] = 'abcd_1234'

        response = self.client.post(self.create_user_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(id=2).first_name, 'fadmin')

    def test_create_user_with_wrong_confirm_password(self):
        data = self.user_data
        data['email'] = 'user2@test.com'
        data['confirm_password'] = 'sdasd'

        response = self.client.post(self.create_user_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_weak_password(self):
        data = self.user_data
        data['email'] = 'user2@test.com'
        data['confirm_password'] = '123456'
        response = self.client.post(self.create_user_url, data, format='json')

        self.assertRaises(exceptions.ValidationError)

        """
        ---- login test cases ----
        """
    def test_login(self):
        login_data = {'email': 'user1@test.com',
                      'password': 'abcd_1234'}

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_credentials(self):
        login_data = {'email': 'user@test.com',
                      'password': 'abcd_1234'}

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertRaises(exceptions.ValidationError)
