"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

VERIFY_EMAIL_ADDRESS = dict()
VERIFY_EMAIL_ADDRESS['subject'] = '[zooniverse] Please verify your email address'
VERIFY_EMAIL_ADDRESS['message'] = '<p>Dear {{title}} {{first_name}} {{last_name}}</p>' \
                                  '<p>We have received a new account request with our zooniverse system from this' \
                                  'email address. Please verify your email address by clicking on the following ' \
                                  '<a href="{{link}}" target="_blank">link</a>:</p>' \
                                  '<p><a href="{{link}}" target="_blank">{{link}}</a></p>' \
                                  '<p>If you believe that the email has been sent by mistake or you have not ' \
                                  'requested for an account please <strong>do not</strong> click on the link.</p>' \
                                  '<p>Alternatively you can report this incident to <a ' \
                                  'href="mailto:support@zooniverse.com" target="_top">support@zooniverse.com</a> for ' \
                                  'investigation.</p>' \
                                  '<p>&nbsp;</p>' \
                                  '<p>Regards,</p>' \
                                  '<p>zooniverse Team</p>'
