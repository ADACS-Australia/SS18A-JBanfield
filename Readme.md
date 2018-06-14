**Project Overview**
====================

The aim of the project is to facilitate user interface for the radio galaxy zooniverse (Banfield+)
where the users will be able to provide labels for images of galaxies to be fed to an active learning 
recommandation package. This project is currently made using the django framework.

Prerequisites
=============
- Python 3
- MySQL 5.7+ (tested with 5.7)

*Optional*
- Docker and Docker-Compose

Setup
=====

## Configuration Steps ##
The required steps include the following:
1. `virtualenv venv` (create the virtual environment, e.g. with https://docs.python.org/3/library/venv.html or https://github.com/pyenv/pyenv)
2. `git pull` (clone the code)
3. `source venv/bin/activate` (activate the virtual environment)
4. `cd zooniverse/zooniverse/settings` (enter the settings directory)
5. `touch local.py` (create the file for local settings - refer to the *Local Settings* section
for setting up a local settings file)
6. `cd ../../` (enter the root directory of the project)
7. `pip3 install -r requirements.txt` (install required python packages)
8. `./development-manage.py migrate` (migrate, for staging or production 
9. `./development-manage.py createsuperuser` (create an admin account)
specify the required manage.py file instead)
10. `./development-manage.py setup` (sets up the project, most directory structure for now)
11. `./development-manage.py images` (optional - download all images for the catalog. For ~9000 images, expect about two hours on a high speed connection.)
12. `./development-manage.py runserver 8000` (running the server)

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
    MEDIA_ROOT = 'media/'   # The location on disk, set this to the location of the shared mounted filesystem
    ```

2. The secret key used to authenticate the workflow with the UI API (can be generated with e.g. https://www.miniwebtool.com/django-secret-key-generator/)
    ```python
    SECRET_KEY = 'some really long string with $YMb0l$'
    ```

3. The admins of the site who will receive error emails.
    ```python
    ADMINS = [
        ('Your Name', 'youremail@dd.ress'),
    ]
    
    MANAGERS = ADMINS
    ```

4. The address from where the server emails will be sent.
    ```python
    SERVER_EMAIL = 'serveremail@dd.ress'
    ```

5. The address from where the notification emails will be sent.
    ```python
    EMAIL_FROM = 'mail@dd.ress'
    ```

6. Other email settings can also be provided.
    ```python
    EMAIL_HOST = 'gpo.dd.res'
    EMAIL_PORT = 25
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    ```
    
7. Database settings. For example, a simple MySQL database can be configured using
    ```python
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zooniverse_dev',
        'USER': 'django',
        'PASSWORD': 'test-password#1',
        'HOST': 'db',
        'PORT': 3306,
        }
    }
    ```
    
8. Set the login redirect url (optional). Set the page you want the user to see after login. If not set, it redirects to
`/accounts/profile/`
    ```python
    LOGIN_REDIRECT_URL = '/'
    ```

(Optional) Force the https protocol even if the request is not secure
in links. Specially helpful in case server is hosted on a different 
machine and apache redirect is sent there.
```python
HTTP_PROTOCOL = 'https'
```
