import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



def split_string(input_string):
    # Split the string into a list using the comma as a delimiter
    try:
        if input_string.strip() == '':
            return []
        result_list = input_string.split(',')
    except:
        raise ValueError(f"Invalid input string: {input_string}")
    result_list = [x.strip() for x in result_list]
    return result_list


# Likely switch to Amazon Simple Email Service (Amazon SES)
# when Bottle Service has its own domain and email address
class EmailMessager:
    # Set your SendGrid API key
    def __init__(self, api_key, from_email):
        self.sendgrid_api_key = api_key
        self.from_email = from_email

    # Send an email
    def send_email(self, recipient_email, subject, message):
        # Create a SendGrid Mail object
        message = Mail(
            from_email=self.from_email,
            to_emails=recipient_email,
            subject=subject,
            plain_text_content=message
        )

        # Initialize the SendGrid API client
        sg = SendGridAPIClient(self.sendgrid_api_key)

        # Send the email
        response = sg.send(message)

        # Print the status code and body of the response
        print("Status Code:", response.status_code)
        print("Response Body:", response.body)
