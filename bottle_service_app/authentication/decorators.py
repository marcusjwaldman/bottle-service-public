# Authentication Decorator that excepts a list of roles
from django.shortcuts import render, redirect

from authentication.enums import BottleServiceAccountType
from authentication.exceptions import AuthenticationExpiredException, AuthenticationMissingException
from authentication.models import BottleServiceUser
from authentication.session import BottleServiceSession


def bottle_service_auth(roles):

    def decorator(function):
        def wrap(request, *args, **kwargs):
            print("Authenticating for Protected Webpage...")
            # User not logged in redirect to login page
            try:
                user = BottleServiceSession.get_user(request)
            except AuthenticationExpiredException:
                return redirect('/', {'error': 'Authentication expired. Please login again.'})
            except AuthenticationMissingException:
                return redirect('/')
            except Exception as e:
                print(e)
                return redirect('/', {'error': 'System error. Please, try login again. If the problem persists, '
                                               'contact support.'})
            if not user:
                print("User not in session")
                return redirect('/', {'error': 'System error. Please, try login again. If the problem persists, '
                                               'contact support.'})
            account_type = user.account_type
            if not account_type or not any(r.equals_string(account_type) for r in roles):
                print("User not authorized ")
                raise Exception("User not authorized to access this page")
            # TODO: Add active check

            return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
        return wrap
    return decorator


# Only works when parameters are passed in path
def confirmation_required(message="Please confirm your action"):

    def decorator(function):
        def wrap(request, *args, **kwargs):
            if request.method == 'GET' or request.method == 'POST' and not request.POST.get('confirmation'):
                # If the form is submitted and confirmation is not provided,
                # render the confirmation page
                referring_page = request.META.get('HTTP_REFERER')
                return render(request, 'authentication/confirmation_page.html',
                              {'message': message, 'referring_page': referring_page})
            elif request.method == 'POST' and request.POST.get('confirmation') == 'yes':
                # If the form is submitted and confirmation is 'yes',
                # proceed to the original view
                return function(request, *args, **kwargs)
            else:
                # If the request method confirmation is 'no',
                # redirect back to the original page
                referring_page = request.POST.get('referring_page')
                # Redirect back to the referring page or to a default URL if not available
                return redirect(referring_page or 'default_url')

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
        return wrap
    return decorator
