# Authentication Decorator that excepts a list of roles
from authentication.enums import BottleServiceAccountType
from authentication.models import BottleServiceUser
from authentication.session import BottleServiceSession


def bottle_service_auth(roles):

    def decorator(function):
        def wrap(request, *args, **kwargs):
            print("Authenticating for Protected Webpage...")
            if not BottleServiceSession.has_user(request):
                print("User not in session")
                raise Exception("User not in session")
            user = BottleServiceSession.get_user(request)
            account_type = user.account_type
            if not any(r.equals_string(account_type) for r in roles):
                print("User not authorized")
                raise Exception("User not authorized")

            return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
        return wrap
    return decorator
