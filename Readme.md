**Project Overview**
====================

The aim of this project is to facilitate an enhanced web interface for radio galaxy zoo (Banfield+) allowing users to label galaxy data suggested by an active learning backend ([Acton](https://github.com/chengsoonong/acton)). This project currently builds upon the django framework.

User documentation
==================

User documentation can be found on the wiki (https://github.com/ADACS-Australia/SS18A-JBanfield/wiki). 

Prerequisites
=============
- Python 3
- MySQL 5.7+ (tested with 5.7)
- Redis - for installation refer to Redis quick start page (https://redis.io/topics/quickstart)

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
13. Run the Redis server by using appropriate command depending on the host
14. `celery -A zooniverse worker -l info` in a separate window (start the celery worker)

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
9. Set configurations of the redis server (if you are running it in a different path)
    ```python
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    ```

(Optional) Force the https protocol even if the request is not secure
in links. Specially helpful in case server is hosted on a different 
machine and apache redirect is sent there.
```python
HTTP_PROTOCOL = 'https'
```

Docker
======
In case you choose to run this code as Docker containers, this section provides basic information about how to proceed. 

Before we begin, the following assumes that you have set your local.py file (see previous section). In addition, you will need to modify the two lines related to celery by replacing `localhost` with `redis`, as follows:
```python
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
```

Here are a few steps:

1. Install docker and docker-compose, which can downloaded from: https://docs.docker.com/compose/install/#install-compose
2. Once docker is launched, open a terminal and navigate to the project's repository.

    At the root of the project's repository are included the files `Dockerfile` and `docker-compose.yml`. For all the following steps have to be executed from that repository (or otherwise add the path to the files).

3. From there, type: 
    
    `docker-compose up -d --build`

    This will download Python, MySQL, and install most python packages. Once installed, the container will be launched. It should also run most of the `python development-manage.py <command>` commands for you. 

4. Now that this has finished, type: 
    
    `docker ps` 
    
    This will display the different docker processes currently running (e.g. `dg_zooniverse` and `mysql_zooniverse`). 
    
5. As we want to create a superuser with `development-manage.py`, connect to dg_zooniverse with: 

    `docker exec -ti dg_zooniverse bash`. 

    This will open a new shell where you see the virtual webserver. Here, we can simply type the usual commands that are on the project wiki. So: `python development-manage.py createsuperuser`. This will prompt you to add a username, email and password. 

6. To quit the virtual server, simply type `exit`. The server will still be running.

When running docker in detached mode (using `-d`), allow for a few seconds (this will depend on your computer hardware) for the server to start.

Open a browser, and go to `http://0.0.0.0:8000`. 

If nothing shows up after a minute or two, try `docker-compose restart`. 

To stop all of these processes, type `docker-compose stop`. You can restart it with `docker-compose up -d` (`-d` stands for “detached”, and can be omitted if you wanna see the server’s output).

Note that the database information present in the `docker-compose.yml` file should match the database information in `local.py`.

License
=======

The project is licensed under the MIT License. For more information, please refer to the [LICENSE](https://github.com/ASVO-TAO/ADACS-SS18A-JBanfield/blob/dev/LICENSE) document.


Authors
=======

* [Shibli Saleheen](https://github.com/shiblisaleheen) (as part of [ADACS](https://adacs.org.au/))
* [Dany Vohl](https://github.com/macrocosme) (as part of [ADACS](https://adacs.org.au/))
