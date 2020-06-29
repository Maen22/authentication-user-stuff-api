from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from .forms import UserCreateForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator

from .models import User


def index(request):
    return render(request, 'account/index.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserCreateForm(data=request.POST)
        # profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid():
            user_form.cleaned_data['password'] = user_form.cleaned_data.pop('password1')
            user_form.cleaned_data.pop('password2')
            user = User.objects.create_user(**user_form.cleaned_data)
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'

            # makes an html a string to send it through the email!!!
            message = render_to_string('account/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': user.pk,
                'token': default_token_generator.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account:activation_sent')
    else:
        user_form = UserCreateForm()
        return render(request, 'account/registration.html',
                      {'user_form': user_form,
                       'registered': registered})


def activation_sent_view(request):
    return render(request, 'account/activation_sent.html')


def user_login(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")  # should be notified in the same
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return render(request, 'account/login.html', {'invalid': 'Invalid Credentials'})
    else:
        return render(request, 'account/login.html', {})
