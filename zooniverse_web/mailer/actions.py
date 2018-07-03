"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from __future__ import unicode_literals

from zooniverse_web.mailer import templates, email


def email_verify_request(to_addresses, title, first_name, last_name, link):
    context = {
        'title': title,
        'first_name': first_name,
        'last_name': last_name,
        'link': link,
    }

    email.Email(
        subject=templates.VERIFY_EMAIL_ADDRESS['subject'],
        to_addresses=to_addresses,
        template=templates.VERIFY_EMAIL_ADDRESS['message'],
        context=context,
    ).send_email()
