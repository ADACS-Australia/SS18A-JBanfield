"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class zooniverseWebConfig(AppConfig):
    name = 'zooniverse_web'

    def ready(self):
        import zooniverse_web.signals
