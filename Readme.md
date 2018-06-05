**Project Overview**
====================

The aim of the project is to facilitate user interface for the radio galaxy zooniverse (Banfield+)
where the users will be able to provide labels for images of galaxies to be fed to an active learning 
recommandation package. This project is currently made using the django framework.

Prerequisites
=============
- Python 3
- MySQL or SQLite

*Optional*
- Docker and Docker-Compose

Setup
=====

## Configuration Steps ##
The required steps include the following:
1. `virtualenv venv` (create the virtual environment)
2. `git pull` (clone the code)
3. `source venv/bin/activate` (activate the virtual environment)
4. `cd zooniverse/zooniverse/settings` (enter the settings directory)
5. `touch local.py` (create the file for local settings - refer to the *Local Settings* section
for setting up a local settings file)
6. `cd ../../` (enter the root directory of the project)
7. `./development-manage.py createsuperuser` (create an admin account)
8. `./development-manage.py migrate` (migrate, for staging or production 
specify the required manage.py file instead)
9. `./development-manage.py setup` (sets up the project, most directory structure for now)
10. `./development-manage.py images` (optional - download all images for the catalog, and go get a cup of tea and a nap)
11. `./development-manage.py runserver 8000` (running the server)

## Local Settings ##
The project is required to have customised machine specific settings.
Those settings need to included or overridden in the local settings file.
Create one `local.py` in the settings module next to the other settings
files (`base.py`, `development.py`, `production.py` etc.)

The following settings needs to be present in the `local.py` settings file.

1. The base and media directories:
    ```python
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    MEDIA_URL = '/media/'   # The media URL
    MEDIA_ROOT = '/data/'   # The location on disk, set this to the location of the shared mounted filesystem
    ```

2. The secret key used to authenticate the workflow with the UI API (can be generated with e.g. https://www.miniwebtool.com/django-secret-key-generator/)
    ```python
    WORKFLOW_SECRET = 'some really long string with $YMb0l$'
    ```

3.  Where a user should be redirected after loging in:
    ```python
    LOGIN_REDIRECT_URL='/classify'
    ```

4. The admins of the site who will receive error emails.
    ```python
    ADMINS = [
        ('Your Name', 'youremail@dd.ress'),
    ]
    
    MANAGERS = ADMINS
    ```

5. The address from where the server emails will be sent.
    ```python
    SERVER_EMAIL = 'serveremail@dd.ress'
    ```

6. The address from where the notification emails will be sent.
    ```python
    EMAIL_FROM = 'mail@dd.ress'
    ```

7. Other email settings can also be provided.
    ```python
    EMAIL_HOST = 'gpo.dd.res'
    EMAIL_PORT = 25
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    ```

8. The log file settings.
    ```python
    LOG_DIRECTORY = os.path.join(BASE_DIR, 'path/to/log')
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s %(levelname)s (%(name)s): %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIRECTORY, zooniverse),
                'formatter': 'standard',
                'when': 'midnight',
                'interval': 1,
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file', 'mail_admins'],
                'level': 'INFO',
                'propagate': True,
            },
            'zooniverse_web': {
                'handlers': ['console', 'file', 'mail_admins'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
    ```
    
9. Database settings. For example, a simple SQLite database can be configured using
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, '../db.sqlite3'),
        }
    }
    ```
    or with the following for a MySQL database.
    ```python
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zooniverse_dev',
        'USER': 'django',
        'PASSWORD': 'test-docker_#1',
        'HOST': 'db',
        'PORT': 3306,
        }
    }
    ```
10. The REST framework permissions. E.g.
    ```python
    REST_FRAMEWORK = {
        # Use Django's standard `django.contrib.auth` permissions,
        # or allow read-only access for unauthenticated users.
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
        ]
    ```

(Optional) Force the https protocol even if the request is not secure
in links. Specially helpful in case server is hosted in different 
machine and apache redirect is there.
```python
HTTP_PROTOCOL = 'https'
```
