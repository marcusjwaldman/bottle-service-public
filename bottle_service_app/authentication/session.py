from django.conf import settings

from authentication.enums import BottleServiceAccountType
from authentication.exceptions import AuthenticationMissingException, AuthenticationExpiredException
from authentication.models import BottleServiceUser
from django.utils import timezone

from cart.models import CustomerOrder


class BottleServiceSession:
    user_obj_key = 'user_obj'
    user_last_accessed_key = 'user_last_accessed'
    customer_order_id_key = 'customer_order_id'

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

    @staticmethod
    def store_customer_order_id(request, order_id):
        request.session[BottleServiceSession.customer_order_id_key] = order_id
        request.session[BottleServiceSession.user_last_accessed_key] = timezone.now().isoformat()

    @staticmethod
    def get_customer_order_id(request):
        if BottleServiceSession.customer_order_id_key in request.session:
            return request.session[BottleServiceSession.customer_order_id_key]
        return None

    @staticmethod
    def get_customer_order(request, restaurant):
        customer_order = None
        order_id = BottleServiceSession.get_customer_order_id(request)
        if order_id:
            try:
                customer_order = CustomerOrder.objects.prefetch_related('order_items').get(pk=order_id)
                if customer_order.restaurant != restaurant:
                    print(f'Session customer order {order_id} restaurant menu does not match current restaurant menu. '
                          f'Creating new order.')
                    customer_order = None
            except CustomerOrder.DoesNotExist:
                customer_order = None
        if customer_order is None:
            customer_order = CustomerOrder.objects.create(order_status='empty', total_cost=0,
                                                          restaurant=restaurant)
            BottleServiceSession.store_customer_order_id(request, customer_order.id)
        return customer_order
