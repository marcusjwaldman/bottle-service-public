from django.shortcuts import render

from authentication.enums import BottleServiceAccountType
from authentication.models import BottleServiceUser
from authentication.decorators import bottle_service_auth


@bottle_service_auth(roles=[BottleServiceAccountType.ADMIN])
def administration_home(request):
    if request.method == "GET":
        users = BottleServiceUser.objects.all()
        user_list = list(users)
        context = {'users': user_list}
        print(f'users: {user_list}')
        return render(request, 'administration/administration_home.html', context)
    if request.method == "POST":
        email = request.POST.get('email')
        action = request.POST.get('action')
        context = {}
        try:
            user = BottleServiceUser.objects.get(email=email)
        except BottleServiceUser.DoesNotExist:
            context['error'] = f'User does not exist for email: {email}'
            user = None
        if user:
            if action == "deactivate":
                user.is_active = False
                user.save()
            elif action == "activate":
                user.is_active = True
                user.save()
            elif action == "terminate":
                user.delete()
        users = BottleServiceUser.objects.all()
        user_list = list(users)
        context['users'] = user_list
        return render(request, 'administration/administration_home.html', context)