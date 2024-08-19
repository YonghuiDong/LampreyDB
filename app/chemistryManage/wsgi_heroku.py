# coding: utf-8

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chemistryManage.settings.production")

application = get_wsgi_application()
