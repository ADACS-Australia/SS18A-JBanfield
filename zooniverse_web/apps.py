# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class zooniverseWebConfig(AppConfig):
    name = 'zooniverse_web'

    def ready(self):
        import zooniverse_web.signals
