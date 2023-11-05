from django.contrib.auth.models import User
from django.shortcuts import render, redirect
import requests
from security import PasswordStrength
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession

login_page = 'authentication/login.html'


def redirect_to_account_type(request, account_type):
    if account_type == BottleServiceAccountType.DISTRIBUTOR:
        return redirect('/distributor')
    elif account_type == BottleServiceAccountType.RESTAURANT:
        return redirect('/restaurant')
    elif account_type == BottleServiceAccountType.CUSTOMER:
        return redirect('/customer')
    elif account_type == BottleServiceAccountType.ADMIN:
        return redirect('/administration')
    else:
        context = {'error': 'Invalid account type'}
        return render(request, login_page, context)


def login(request):
    if request.method == "GET":
        if BottleServiceSession.has_user(request) and BottleServiceSession.get_user(request).is_active:
            account_type = BottleServiceSession.get_account_type(request)
            return redirect_to_account_type(request, account_type)
        return render(request, login_page)
    elif request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.get(email=email)

        if not user.check_password(password):
            context = {'error': 'Incorrect password'}
            return render(request, login_page, context)

        if not user.is_active:
            context = {'error': 'User not active'}
            return render(request, login_page, context)

        BottleServiceSession.store_user_obj(request, user)

        account_type = user.account_type
        return redirect_to_account_type(request, account_type)


def logout(request):
    BottleServiceAccountType.clear_session(request)
    return redirect('/')


def account_creation(request):
    if request.method == "GET":
        return render(request, 'authentication/account_creation_email.html')
    elif request.method == "POST":
        email = request.POST.get('email')
        account_type = request.POST.get('account_type')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if email and account_type and password:
            if password != password_confirm:
                context = {'error': 'Passwords do not match'}
                return render(request, 'authentication/account_creation_email.html', context)
            if not PasswordStrength.check_password(password):
                context = {'error': f'Passwords does not meet strength requirements. Password Rules: {PasswordStrength.password_rules()}'}
                return render(request, 'authentication/account_creation_email.html', context)
            user = User.objects.create_user(email=email, account_type=account_type, password=password)
            if user:
                return redirect('/')
            else:
                context = {'error': 'Could not create account. Account with this email may already exists.'}
                return render(request, 'authentication/account_creation_email.html', context)
        elif email:
            if User.objects.get(email=email):
                context = {'error': 'Email already associated with an account'}
                return render(request, 'authentication/account_creation_email.html', context)
            else:
                context = {'email': email}
                return render(request, 'authentication/account_creation_acct_pwd.html', context)
