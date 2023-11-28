from authentication.enums import BottleServiceAccountType
from authentication.models import BottleServiceUser


class BottleServiceSession:
    user_obj_key = 'user_obj'

    @staticmethod
    def has_user(request):
        return BottleServiceSession.user_obj_key in request.session

    @staticmethod
    def get_user(request):
        user = request.session.get(BottleServiceSession.user_obj_key, None)
        if not user:
            return None
        if not isinstance(user, BottleServiceUser):
            user_dict = user
            user = BottleServiceUser.dict_to_user(user_dict)
        user = BottleServiceUser.objects.prefetch_related( 'distributor', 'restaurant', 'customer',
                                                           'distributor__address').get(pk=user.id)
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

    @staticmethod
    def clear_session(request):
        request.session.pop(BottleServiceSession.user_obj_key, None)
