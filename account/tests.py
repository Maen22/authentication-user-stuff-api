from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from rest_framework import status, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from Task1 import settings
from .models import User
import json
from django.core import mail


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
                           'image': 'asdasd'}

        self.user = User.objects.create_user(email='user1@test.com', first_name='fuser', last_name='luser', gender='M',
                                             password='abcd_1234')
        self.admin = User.objects.create_superuser(**self.admin_data)
        self.token = Token.objects.get_or_create(user=self.user)

        # self.client.force_login(self.admin)

        self.create_user_url = reverse('api-create-user')
        self.login_url = reverse('api-login')
        self.change_password_url = reverse('api-change-password')
        self.me_url = reverse('api-me')
        self.admin_list_url = reverse('api-list')
        self.admin_detail_url = reverse('api-detail', args=(1,))
        self.email_activation_url = 'http://127.0.0.1:8000/activate/{}/{}'

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
        self.assertEqual(content['non_field_errors'][0],
                         "This password is too short. It must contain at least 8 characters.")
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

    def test_change_password_with_weak_password(self):
        data = {'old_password': 'abcd_1234', 'new_password': '123456', 'confirm_password': '123456'}
        self.client.force_login(self.user)

        response = self.client.put(self.change_password_url, data)
        content = json.loads(response.content)

        self.assertRaises(exceptions.ValidationError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['non_field_errors'][0],
                         "This password is too short. It must contain at least 8 characters.")
        self.assertEqual(content['non_field_errors'][1], "This password is too common.")
        self.assertEqual(content['non_field_errors'][2], "This password is entirely numeric.")

    def test_change_password_with_unmatch_new_passwords(self):
        data = {'old_password': 'abcd_1234', 'new_password': 'abcd_12345', 'confirm_password': '123456'}
        self.client.force_login(self.user)

        response = self.client.put(self.change_password_url, data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['non_field_errors'][0],
                         "Passwords doesn't match")

    def test_change_password_with_unmatch_old_passwords(self):
        data = {'old_password': 'abcd_12345', 'new_password': 'abcd_12345', 'confirm_password': 'abcd_12345'}
        self.client.force_login(self.user)

        response = self.client.put(self.change_password_url, data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['non_field_errors'][0],
                         "Old password doesn't match")

    """
    ---- users/me/ test cases ----
    """

    """
        ---- 1- users/me/ (GET) ----
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
        ---- 2- users/me/ (PUT) ----
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

    def test_update_email_with_already_existed_email(self):
        data = {'email': 'admin1@test.com',
                'first_name': 'maen',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.user)

        response = self.client.put(self.me_url, data=data)

        content = json.loads(response.content)
        print(content)

        self.assertEqual(content['email'][0], "user with this email already exists.")
        self.assertEqual(response.status_code, 400)

    """
        ---- 3- users/me/ (PATCH) ----
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
        ---- 4- users/me/ (DELETE) ----
    """

    def test_delete_user(self):
        self.client.force_login(self.user)

        response1 = self.client.delete(self.me_url)
        self.assertEqual(response1.status_code, 204)

        self.user.refresh_from_db()

        self.assertEqual(self.user.is_active, False)

        response2 = self.client.delete(self.me_url)
        self.assertEqual(response2.status_code, 403)

    """
    ---- users/ test cases for the admins ----
    """

    """
        ---- 1- users/ (GET) (list) ----
    """

    def test_list_all_users(self):
        self.client.force_login(self.admin)

        response = self.client.get(self.admin_list_url)

        content = response.json()

        keys = ["id", "email", "first_name", "last_name", "gender"]  # ////// use zip() func
        for x in range(User.objects.count()):
            for key in keys:
                value = getattr(User.objects.get(id=x + 1), key)
                assert value == content[x][key]

        self.assertEqual(response.status_code, 200)

    def test_list_all_users_by_normal_user(self):
        self.client.force_login(self.user)

        response = self.client.get(self.admin_list_url)

        content = response.json()

        self.assertEqual(content['detail'], "You do not have permission to perform this action.")
        self.assertEqual(response.status_code, 403)

    """
        ---- 2- users/{id} (GET) (detail) ----
    """

    def test_get_user_detail(self):
        self.client.force_login(self.admin)

        response = self.client.get(self.admin_detail_url)

        content = response.json()
        print(content)

        keys = ["id", "email", "first_name", "last_name", "gender"]
        for key in keys:
            value = getattr(User.objects.get(id=1), key)
            assert value == content[key]
        print(content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_detail_by_normal_user(self):
        self.client.force_login(self.user)

        response = self.client.get(self.admin_detail_url)

        content = response.json()

        self.assertEqual(content['detail'], "You do not have permission to perform this action.")
        self.assertEqual(response.status_code, 403)

    def test_get_user_detail_for_unknown_user(self):
        self.client.force_login(self.admin)
        self.admin_detail_url = reverse('api-detail', args=(3,))

        response = self.client.get(self.admin_detail_url)
        content = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(content['detail'], "Not found.")

    """
        ---- 3- users/{id} (PUT) (detail) ----
    """

    def test_update_user_details_by_admin(self):
        data = {'email': 'user12345@test.com',
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.admin)
        response = self.client.put(self.admin_detail_url, data=data)

        self.user.refresh_from_db()

        content = json.loads(response.content)
        keys = ["email", "first_name", "last_name", "gender"]
        for k in keys:
            value = getattr(self.user, k)
            assert value == content[k]
        self.assertEqual(response.status_code, 200)

    def test_update_user_details_by_normal_user(self):
        data = {'email': 'user12345@test.com',
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.user)
        response = self.client.put(self.admin_detail_url, data=data)
        content = response.json()

        self.assertEqual(content['detail'], "You do not have permission to perform this action.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_unknown_user_detail_by_admin(self):
        self.client.force_login(self.admin)
        self.admin_detail_url = reverse('api-detail', args=(3,))

        response = self.client.put(self.admin_detail_url)
        content = response.json()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(content['detail'], "Not found.")

    def test_update_user_details_by_admin_null_or_blank_or_invalid_email(self):
        # null email
        data = {'email': None,
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.admin)
        response = self.client.put(self.admin_detail_url, data=data)
        content = json.loads(response.content)

        self.assertEqual(content['email'][0], "This field may not be null.")
        self.assertRaises(exceptions.ValidationError)

        # blank email
        data['email'] = ''
        response = self.client.put(self.admin_detail_url, data=data)
        content = json.loads(response.content)

        # invalid email
        data['email'] = 'maensda'
        response = self.client.put(self.admin_detail_url, data=data)
        content = json.loads(response.content)

        self.assertEqual(content['email'][0], "Enter a valid email address.")

    def test_update_user_details_by_admin_missing_field(self):
        data = {'email': 'maen@test.com',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.admin)

        response = self.client.put(self.admin_detail_url, data=data)

        content = json.loads(response.content)

        self.assertEqual(content['first_name'][0], "This field is required.")
        self.assertEqual(response.status_code, 400)

    def test_update_user_details_by_admin_with_password(self):
        data = {'email': "user123@test.com",
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'password': 'maen_12345',
                'image': None}

        self.client.force_login(self.admin)
        response = self.client.put(self.admin_detail_url, data=data)

        self.user.refresh_from_db()

        # The password should not be affected by ('PUT', or 'PATCH')
        self.assertNotEqual(self.user.check_password(data['password']), True)

    """
        ---- 4- users/{id} (PATCH) (detail) ----
    """

    def test_partial_update_user_details_by_admin(self):
        data = {'email': 'user12345@test.com',
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M'}

        self.client.force_login(self.admin)
        response = self.client.patch(self.admin_detail_url, data=data)

        User.objects.get(id=1).refresh_from_db()

        content = json.loads(response.content)
        print(content)
        keys = ["email", "first_name", "last_name", "gender"]
        for k in keys:
            value = getattr(User.objects.get(id=1), k)
            assert value == content[k]

        self.assertEqual(response.status_code, 200)

    def test_partial_update_user_details_by_admin_with_password(self):
        data = {'email': "user123@test.com",
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'password': 'maen_12345',
                'image': None}

        self.client.force_login(self.admin)
        response = self.client.put(self.admin_detail_url, data=data)

        self.user.refresh_from_db()

        # The password should not be affected by ('PUT', or 'PATCH')
        self.assertNotEqual(self.user.check_password(data['password']), True)

    def test_partial_update_user_details_by_normal_user(self):
        data = {'email': 'user12345@test.com',
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M'}

        self.client.force_login(self.user)

        response = self.client.patch(self.admin_detail_url, data=data)
        content = json.loads(response.content)
        print(content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content['detail'], "You do not have permission to perform this action.")

    def test_partial_update_user_details_null_or_blank_or_invalid_email(self):
        # null email
        data = {'email': None,
                'first_name': 'updated fname',
                'last_name': 'updated lname',
                'gender': 'M',
                'image': None}

        self.client.force_login(self.admin)
        response = self.client.patch(self.admin_detail_url, data=data)
        content = json.loads(response.content)

        self.assertEqual(content['email'][0], "This field may not be null.")
        self.assertRaises(exceptions.ValidationError)

        # blank email
        data['email'] = ''
        response = self.client.put(self.admin_detail_url, data=data)
        content = json.loads(response.content)

        # invalid email
        data['email'] = 'maensda'
        response = self.client.put(self.admin_detail_url, data=data)
        content = json.loads(response.content)

        self.assertEqual(content['email'][0], "Enter a valid email address.")

    """
        ---- 5- users/{id} (DELETE) (detail) ----
    """

    def test_delete_user_by_admin(self):
        self.client.force_login(self.admin)

        response1 = self.client.delete(self.admin_detail_url)
        self.assertEqual(response1.status_code, 204)

        self.user.refresh_from_db()

        self.assertEqual(self.user.is_active, False)

        response2 = self.client.delete(self.admin_detail_url)
        # self.assertEqual(response2.status_code, 403)

        print(response2.status_code)

    def test_delete_user_by_normal_user(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.admin_detail_url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.user.is_active, True)

    def test_delete_unknown_user_by_admin(self):
        self.client.force_login(self.admin)
        admin_detail_url = reverse('api-detail', args=(3,))

        response = self.client.delete(admin_detail_url)
        content = response.json()

        self.assertEqual(response.status_code, 404)

    """
    ---- activate/ test cases for the email activation ----
    """

    def test_email_sending(self):
        user = User.objects.create_user(email='testuser@test.com', first_name='fuser', last_name='luser', gender='M',
                                        password='abcd_1234')

        token = default_token_generator.make_token(user)
        mail_subject = 'Activate your account.'
        message = 'http://127.0.0.1:8000/activate/{}/{}/'.format(user.id, token)
        to_email = user.email
        mail.send_mail(
            mail_subject, message,
            settings.EMAIL_HOST_USER, [to_email]
        )

        self.assertEqual(user.is_active, False)

        response = self.client.get(str(mail.outbox[0].body))
        content = response.json()
        user.refresh_from_db()

        self.assertEqual(response.status_code, 202)
        self.assertEqual(user.is_active, True)
        self.assertEqual(content, "Thank you for your email confirmation. Now you can login your account.")

    def test_email_sending_with_invalid_token(self):
        user = User.objects.create_user(email='testuser@test.com', first_name='fuser', last_name='luser', gender='M',
                                        password='abcd_1234')

        token = default_token_generator.make_token(user)
        mail_subject = 'Activate your account.'
        message = 'http://127.0.0.1:8000/activate/{}/{}/'.format(user.id, token + "asdasd")  # invalid token
        to_email = user.email
        mail.send_mail(
            mail_subject, message,
            settings.EMAIL_HOST_USER, [to_email]
        )

        self.assertEqual(user.is_active, False)

        response = self.client.get(str(mail.outbox[0].body))
        content = response.json()
        user.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(user.is_active, False)
        self.assertEqual(content, "Activation link is invalid!")

    def test_email_sending_with_invalid_id(self):
        user = User.objects.create_user(email='testuser@test.com', first_name='fuser', last_name='luser', gender='M',
                                        password='abcd_1234')

        token = default_token_generator.make_token(user)
        mail_subject = 'Activate your account.'
        message = 'http://127.0.0.1:8000/activate/{}/{}/'.format(10, token)  # invalid token
        to_email = user.email
        mail.send_mail(
            mail_subject, message,
            settings.EMAIL_HOST_USER, [to_email]
        )

        self.assertEqual(user.is_active, False)

        response = self.client.get(str(mail.outbox[0].body))
        content = response.json()
        user.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(user.is_active, False)
        self.assertEqual(content['detail'], "Not found.")
