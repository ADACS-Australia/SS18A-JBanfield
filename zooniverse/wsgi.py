"""
Distributed under the MIT License. See LICENSE.txt for more info.

WSGI config for zooniverse project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zooniverse.settings")

application = get_wsgi_application()
