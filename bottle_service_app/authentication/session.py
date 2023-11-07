class BottleServiceSession:
    user_obj_key = 'user_obj'

    @staticmethod
    def has_user(request):
        return BottleServiceSession.user_obj_key in request.session

    @staticmethod
    def get_user(request):
        return request.session.get(BottleServiceSession.user_obj_key, None)

    @staticmethod
    def get_account_type(request):
        user_obj = BottleServiceSession.get_user(request)
        if user_obj:
            return user_obj.account_type
        return None

    @staticmethod
    def store_user_obj(request, user_obj):
        request.session[BottleServiceSession.user_obj_key] = user_obj

    @staticmethod
    def clear_session(request):
        request.session.pop(BottleServiceSession.user_obj_key, None)
