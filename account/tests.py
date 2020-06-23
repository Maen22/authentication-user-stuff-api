from django.urls import reverse
from rest_framework import status, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from .models import User
import json


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
                          'password': 'abcd_1234',
                          'image': None}

        self.admin_data = {'email': 'admin1@test.com',
                           'first_name': 'fadmin',
                           'last_name': 'ladmin',
                           'gender': 'M',
                           'password': 'abcd_1234',
                           'image': None}

        self.user = User.objects.create_user(email='user1@test.com', first_name='fuser', last_name='luser', gender='M',
                                             password='abcd_1234')
        self.admin = User.objects.create_superuser(**self.admin_data)
        self.token = Token.objects.get_or_create(user=self.user)

        # self.client.force_login(self.admin)

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
        content = json.loads(response.content)
        user = User.objects.get(email='user2@test.com')

        keys = ['email', 'first_name', 'last_name', 'gender']
        for k in keys:
            value = getattr(user, k)
            assert value == content[k]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(id=2).first_name, 'fadmin')

    def test_create_user_with_existing_email(self):
        data = self.user_data
        data['confirm_password'] = 'abcd_1234'

        response = self.client.post(self.create_user_url, data, format='json')
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['email'][0], "user with this email already exists.")

    def test_create_user_with_wrong_confirm_password(self):
        data = self.user_data
        data['email'] = 'user2@test.com'
        data['confirm_password'] = 'asdbasd'

        response = self.client.post(self.create_user_url, data, format='json')
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['non_field_errors'][0], "Passwords doesn't match, Try again")

    def test_create_user_with_weak_password(self):
        data = self.user_data
        data['email'] = 'user2@test.com'
        data['password'] = '123456'
        data['confirm_password'] = '123456'

        response = self.client.post(self.create_user_url, data, format='json')
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['non_field_errors'][0], "This password is too short. It must contain at least 8 characters.")
        self.assertEqual(content['non_field_errors'][1], "This password is too common.")
        self.assertEqual(content['non_field_errors'][2], "This password is entirely numeric.")

    def test_create_user_with_null_email(self):
        data = self.user_data
        data['email'] = None
        data['confirm_password'] = 'abcd_1234'

        response = self.client.post(self.create_user_url, data, format='json')
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['email'][0], "This field may not be null.")

    def test_create_user_with_null_password(self):
        data = self.user_data
        data['email'] = 'user2@test.com'
        data['password'] = None
        data['confirm_password'] = 'abcd_1234'

        response = self.client.post(self.create_user_url, data, format='json')
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['password'][0], "This field may not be null.")

    def test_create_user_with_blank_email(self):
        data = self.user_data
        data['email'] = ''
        data['confirm_password'] = 'abcd_1234'

        response = self.client.post(self.create_user_url, data, format='json')
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['email'][0], "This field may not be blank.")

    def test_create_user_with_blank_password(self):
        data = self.user_data
        data['email'] = 'user2@test.com'
        data['password'] = ''
        data['confirm_password'] = 'abcd_1234'

        response = self.client.post(self.create_user_url, data, format='json')
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['password'][0], "This field may not be blank.")

    """
    ---- login test cases ----
    """

    def test_login(self):
        login_data = {'email': 'user1@test.com',
                      'password': 'abcd_1234'}

        response = self.client.post(self.login_url, login_data, format='json')
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('(<Token: ' + content['token'] + ">, True)", str(self.token))
        self.assertEqual(content['user_id'], self.user.id)

    def test_login_with_wrong_credentials(self):
        login_data = {'email': 'user@test.com',
                      'password': 'abcd_1234'}

        response = self.client.post(self.login_url, login_data, format='json')
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(content['detail'], "Unable to authenticate with provided credentials")

    def test_login_with_no_credentials(self):
        # login_data = {'email': 'user@test.com',
        #               'password': 'abcd_1234'}

        response = self.client.post(self.login_url, {}, format='json')
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(content['email'][0], "This field is required.")
        self.assertEqual(content['password'][0], "This field is required.")

    """
    ---- password change test cases ----
    """

    def test_change_password_for_authenticated_user(self):
        data = {'old_password': 'abcd_1234', 'new_password': 'abcd_12345', 'confirm_password': 'abcd_12345'}
        self.client.force_login(self.user)

        response = self.client.put(self.change_password_url, data)

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.check_password(data['new_password']), True)

    def test_change_password_for_unauthenticated_user(self):
        data = {'old_password': 'abcd_1234', 'new_password': 'abcd_12', 'confirm_password': 'abcd_12'}
        # self.client.force_login(self.user)

        response = self.client.put(self.change_password_url, data)
        content = json.loads(response.content)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(content['detail'], "Authentication credentials were not provided.")

    """
    ---- users/me test cases ----
    """

    """
    ---- 1- users/me (GET) ----
    """

    def test_get_user_detail(self):
        self.client.force_login(self.user)

        response = self.client.get(self.me_url)
        content = json.loads(response.content)

        keys = ['email', 'first_name', 'last_name', 'gender']
        for k in keys:
            value = getattr(self.user, k)
            assert value == content[k]

        self.assertEqual(response.status_code, 200)

    def test_get_user_detail_with_unauthenticated_user(self):
        response = self.client.get(self.me_url)

        content = json.loads(response.content)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(content['detail'], "Authentication credentials were not provided.")

    def test_get_user_detail_check_response_content(self):
        self.client.force_login(self.user)

        response = self.client.get(self.me_url)
        content_str = response.content.decode("UTF-8")
        content = json.loads(content_str)
        keys = ["email", "first_name", "last_name", "gender", "image"]
        for k in keys:
            value = getattr(self.user, k)
            assert value == content[k]

    """
    ---- 2- users/me (PUT) ----
    """

    def test_update_user_details(self):
        data = {'email': 'user123@test.com',
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.user)
        response = self.client.put(self.me_url, data=data)
        self.user.refresh_from_db()

        content = json.loads(response.content)
        keys = ["email", "first_name", "last_name", "gender"]
        for k in keys:
            value = getattr(self.user, k)
            assert value == content[k]
        self.assertEqual(response.status_code, 200)

    def test_update_user_details_null_or_blank_or_invalid_email(self):

        # null email
        data = {'email': None,
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.user)
        response = self.client.put(self.me_url, data=data)
        content = json.loads(response.content)

        self.assertEqual(content['email'][0], "This field may not be null.")
        self.assertRaises(exceptions.ValidationError)

        # blank email
        data['email'] = ''
        response = self.client.put(self.me_url, data=data)
        content = json.loads(response.content)

        # invalid email
        data['email'] = 'maensda'
        response = self.client.put(self.me_url, data=data)
        content = json.loads(response.content)

        self.assertEqual(content['email'][0], "Enter a valid email address.")

    def test_update_user_details_with_password(self):
        data = {'email': "user123@test.com",
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'password': 'maen_12345',
                'image': None}

        self.client.force_login(self.user)
        response = self.client.put(self.me_url, data=data)

        self.user.refresh_from_db()

        # The password should not be affected by ('PUT', or 'PATCH')
        self.assertNotEqual(self.user.check_password(data['password']), True)

    def test_update_user_details_missing_field(self):
        data = {'email': 'maen@test.com',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.user)

        response = self.client.put(self.me_url, data=data)

        content = json.loads(response.content)

        self.assertEqual(content['first_name'][0], "This field is required.")
        self.assertEqual(response.status_code, 400)

        # Using ('PUT') means changing every single field


    """
    ---- 3- users/me (PATCH) ----
    """

    def test_partial_update_user_details(self):
        data = {'email': 'maen@test.com',
                'last_name': 'updated lname',
                'gender': 'M'}

        self.client.force_login(self.user)
        response = self.client.patch(self.me_url, data=data)

        self.user.refresh_from_db()

        content = json.loads(response.content)
        keys = ["email", "last_name", "gender"]
        for k in keys:
            value = getattr(self.user, k)
            assert value == content[k]

        # Using ('PATCH') means changing any field/s
        self.assertEqual(response.status_code, 200)

    def test_partial_update_user_details_with_password(self):
        data = {'email': None,
                'first_name': 'updated fname',
                'gender': 'M',
                'password': 'maen_12345',
                'image': None}

        self.client.force_login(self.user)
        response = self.client.patch(self.me_url, data=data)

        # The password should not be affected by ('PUT', or 'PATCH')
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.check_password(data['password']), True)

        """
        ---- 4- users/me (DELETE) ----
        """

    def test_delete_user(self):
        self.client.force_login(self.user)

        response1 = self.client.delete(self.me_url)

        # self.assertEqual(content1['detail'], "User deactivated")

        self.assertEqual(response1.status_code, 204)

        self.user.refresh_from_db()

        response2 = self.client.delete(self.me_url)
        self.assertEqual(response2.status_code, 403)
