from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy

'''
    User Model Test Cases
'''


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        # Test creating a new user with an email -> is successful

        email = 'm3n@gmail.com'
        password = 'pass123'
        first_name = 'Maen'
        last_name = 'Ibreigheith'
        gender = 'M'
        user = get_user_model().objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test the email for a new user is normalized

        email = 'm3n@GMAIL.Com'
        user = get_user_model().objects.create_user(
            email=email,
            first_name='Maen',
            last_name='Ibreigheith',
            gender='M',
            password='pass123'
        )

        self.assertEqual(user.email, email.lower())

    def test_user_invalid_email(self):
        # Test creating user with no email raises error

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                first_name='Maen',
                last_name='Ibreigheith',
                gender='M',
                password='pass123'
            )

    def test_create_new_super_user(self):
        # Test creating a new super user
        user = get_user_model().objects.create_superuser(
            email='m3n@hotmail.com',
            first_name='Maen',
            last_name='Ibreigheith',
            gender='M',
            password='pass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


'''
     Admin Site Test Cases
'''


class AdminSiteTests(TestCase):
    # This function will run before any Admin Site Test run (setUp)

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='m3n@hotmail.com',
            first_name='Maen',
            last_name='Ibreigheith',
            gender='M',
            password='pass123'
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='seif@gmail.com',
            first_name='Seif',
            last_name='Obied',
            gender='M',
            password='pass123'
        )

    def test_users_listed(self):
        # Test that users are listed on user page

        url = reverse('admin:account_account_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.first_name)
        self.assertContains(res, self.user.gender)
