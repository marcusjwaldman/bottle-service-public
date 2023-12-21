from django.conf import settings

from authentication.enums import BottleServiceAccountType
from authentication.exceptions import AuthenticationMissingException, AuthenticationExpiredException
from authentication.models import BottleServiceUser
from django.utils import timezone


class BottleServiceSession:
    user_obj_key = 'user_obj'
    user_last_accessed_key = 'user_last_accessed'

    @staticmethod
    def has_user(request):
        return BottleServiceSession.user_obj_key in request.session

    @staticmethod
    def get_user(request):
        # check last access
        last_accessed = request.session.get(BottleServiceSession.user_last_accessed_key)
        if not last_accessed:
            BottleServiceSession.clear_session(request)
            raise AuthenticationMissingException()
        if (timezone.now() - timezone.datetime.fromisoformat(last_accessed) >
                timezone.timedelta(minutes=int(settings.AUTH_TIMEOUT_MINUTES))):
            BottleServiceSession.clear_session(request)
            raise AuthenticationExpiredException()

        user = request.session.get(BottleServiceSession.user_obj_key, None)
        if not user:
            raise AuthenticationMissingException()
        if not isinstance(user, BottleServiceUser):
            user_dict = user
            user = BottleServiceUser.dict_to_user(user_dict)
        user = BottleServiceUser.objects.prefetch_related('distributor', 'restaurant', 'customer',
                                                           'distributor__address').get(pk=user.id)
        # update last access
        request.session[BottleServiceSession.user_last_accessed_key] = timezone.now().isoformat()
        return user

    @staticmethod
    def get_account_type(request):
        user_obj = BottleServiceSession.get_user(request)
        if user_obj:
            return BottleServiceAccountType.get_enum_from_string(user_obj.account_type)
        return None

    @staticmethod
    def store_user_obj(request, user_obj):
        request.session[BottleServiceSession.user_obj_key] = user_obj
        request.session[BottleServiceSession.user_last_accessed_key] = timezone.now().isoformat()

    @staticmethod
    def clear_session(request):
        request.session.pop(BottleServiceSession.user_obj_key, None)
        request.session.pop(BottleServiceSession.user_last_accessed_key, None)
