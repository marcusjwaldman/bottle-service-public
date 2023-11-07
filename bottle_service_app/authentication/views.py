from django.contrib.auth.models import User
from django.shortcuts import render, redirect
import requests
from .security import PasswordStrength, VerificationCode
from authentication.enums import BottleServiceAccountType
from authentication.session import BottleServiceSession
from authentication.models import BottleServiceUser

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

        try:
            user = BottleServiceUser.objects.get(email=email)
        except BottleServiceUser.DoesNotExist:
            context = {'error': 'Incorrect email'}
            return render(request, login_page, context)

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
        print(f'email: {email}')
        account_type = request.POST.get('account_type')
        print(f'account_type: {account_type}')
        password = request.POST.get('password')
        print(f'password: {password}')
        password_confirm = request.POST.get('password_confirm')
        print(f'password_confirm: {password_confirm}')
        verification_code = request.POST.get('verification_code')
        print(f'verification_code: {verification_code}')

        if email and account_type and password and verification_code:
            if password != password_confirm:
                context = {'error': 'Passwords do not match'}
                return render(request, 'authentication/account_creation_email.html', context)
            if not PasswordStrength.check_password(password):
                context = {'error': f'Passwords does not meet strength requirements. Password Rules: {PasswordStrength.password_rules()}'}
                return render(request, 'authentication/account_creation_email.html', context)
            if not VerificationCode.check_code(request, verification_code, email):
                context = {'error': 'Invalid verification code'}
                return render(request, 'authentication/account_creation_email.html', context)
            user = BottleServiceUser.objects.create_user(email=email, account_type=account_type, password=password)
            if user:
                return redirect('/')
            else:
                context = {'error': 'Could not create account. Account with this email may already exists.'}
                return render(request, 'authentication/account_creation_email.html', context)
        elif email:
            if BottleServiceUser.objects.filter(email=email).exists():
                context = {'error': 'Email already associated with an account'}
                return render(request, 'authentication/account_creation_email.html', context)
            else:
                verification_code = VerificationCode.generate()
                VerificationCode.store_code(request, verification_code, email)
                VerificationCode.notify_code(request, email, verification_code)
                context = {'email': email}
                return render(request, 'authentication/account_creation_acct_pwd.html', context)
