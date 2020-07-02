import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Task1.settings')

import django

django.setup()
from account.models import User
from organization.models import Organization


def populate():
    organizations = [
        {"name": "Asqweqwal",
         "location": "Rmallah",
         'phone': 78134},
        {"name": "Extyutitwalt",
         "location": "Rawabi",
         'phone': 7822134},
        {"name": "asdasd",
         "location": "Rawabi",
         'phone': 7822134},
        {"name": "Exaasdlt",
         "location": "Rawabi",
         'phone': 7822134},
        {"name": "asqweqwe",
         "location": "Rawabi",
         'phone': 7822134},
        {"name": "wqeasdasf",
         "location": "Rawabi",
         'phone': 7822134},
        {"name": "asdgadgqwe",
         "location": "Rawabi",
         'phone': 7822134},
        {"name": "asdqwetrgf",
         "location": "Rawabi",
         'phone': 7822134},
        {"name": "xcvxcv",
         "location": "Rawabi",
         'phone': 7822134},
        {"name": "qwe3qwer",
         "location": "Rawabi",
         'phone': 7822134},

    ]
    users = [
        {'email': 'maen@user.com',
         'first_name': "maen",
         'last_name': "adham",
         'gender': 'M',
         'password': '1234',

         },
        {'email': 'maen@asdasd.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },

        {'email': 'asdasd@m3n22.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },

        {'email': 'awqeqwn@m3n22.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },
        {'email': 'maen@qweqwe.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },
        {'email': 'maen@asdasasd.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },
        {'email': 'user1@test.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },
        {'email': 'user2@test.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },
        {'email': 'user3@test.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },
        {'email': 'user4@test.com',
         'first_name': "Adham",
         'last_name': "Maen",
         'gender': 'M',
         'password': '1234',
         },
    ]

    for organization in organizations:
        add_org(organization["name"], organization["location"], organization['phone'])

    # for user in users:
    #     add_user(user["email"], user["first_name"], user["last_name"], user['gender'], user['password'])


def add_org(name, location, phone):
    org = Organization()
    org.name = name
    org.location = location
    org.phone = phone
    org.save()
    return org


def add_user(email, first_name, last_name, gender, password):
    usr = User()
    usr.email = email
    usr.first_name = first_name
    usr.last_name = last_name
    usr.gender = gender
    usr.set_password(password)
    usr.organization = Organization.objects.get(pk=1)
    # usr.is_admin = True
    usr.is_active = True
    # usr.is_staff=True
    usr.save()
    return usr


# Start execution here!
if __name__ == '__main__':
    print("Starting Task1 population script...")
    populate()
    print("Done !")
