**Bottle Service**

Bottle Service is the basis of a Python/Django web-based application that matches Restaurants and Liquor Distributors by geographical locations to form partnerships. Customers can then order from a menu customized for each partnership pair.

**Versions**

The application was written using Python 3.10 and Django 4.2.7.

All other Python dependencies can be found in the `requirements.txt` file.

**Environments**

The application has been configured to run in two environments: Local and AWS.

Set the environmental variable `DJANGO_SETTINGS_MODULE` to determine the environment.

_Local_  
`DJANGO_SETTINGS_MODULE=bottle_service_app.settings_local`

_AWS_  
`DJANGO_SETTINGS_MODULE=bottle_service_app.settings_aws`

**Environmental Variables**

Additional environmental variables must be in place as well:

- `DJANGO_SECRET_KEY` - Randomly generated key unique to your service. Keep this key private.
- `MAIL_API_KEY` - SendGrid API Key. Must have or create a SendGrid account.
- `MAIL_SENDER` - Sender associated with the SendGrid account.
- `MAP_API_KEY` - API Key generated for Google Maps.

**Warning**

This code is not production-ready and is only intended as a starting point, as some features and key security measures have not yet been implemented.

**TODO**

* Notifications - Send messages between partners.
* Gracefully Handle Dissolved Partnerships.
* Handle Profile Changes that no longer match partner criteria.
* Persistent Verification Codes.
* Gracefully Handle Uncaught Exceptions.
* Use S3 for Static Images (AWS).
* Fix QRC Bug - If DNS name changes, the old QRC image does not work.
