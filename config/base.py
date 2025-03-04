# config/base.py (Settings Base, inherited by local.py)
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

import datetime
import glob
import json
# import logging
import os
import pathlib
import re
from django.core.exceptions import ImproperlyConfigured
from django.db import connection

# Consider switching to the way that Two Scoops of Django 1.8 suggests file path handling, section 5.6
# from unipath import Path


# SECURITY WARNING: don't run with debug turned on in production!
# Override in local.py for development
DEBUG = False

# Load JSON-based environment_variables if available
json_environment_variables = {}
try:
    with open("config/environment_variables.json") as f:
        json_environment_variables = json.loads(f.read())
except Exception as e:
    pass
    # print "base.py: environment_variables.json missing"
    # Can't use logger in the settings file due to loading sequence


def get_environment_variable(var_name, json_environment_vars=json_environment_variables):
    """
    Get the environment variable or return exception.
    From Two Scoops of Django 1.8, section 5.3.4
    """
    try:
        return json_environment_vars[var_name]  # Loaded from array above
    except KeyError:
        # variable wasn't found in the JSON environment variables file, so now look in the server environment variables
        pass
        # print "base.py: failed to load {} from JSON file".format(var_name)  # Can't use logger in the settings file

    try:
        # Environment variables can be set with this for example: export GOOGLE_CIVIC_API_KEY=<API KEY HERE>
        return os.environ[var_name]
    except KeyError:
        # Can't use logger in the settings file due to loading sequence
        error_msg = "Unable to set the {} variable from os.environ or JSON file".format(var_name)
        raise ImproperlyConfigured(error_msg)


def get_environment_variable_default(var_name, default_value):
    try:
        return os.environ[var_name]
    except KeyError:
        return default_value


def get_python_version():
    version = os.popen('python --version').read().strip().replace('Python', '')
    print('Python version: ' + version)    # Something like 'Python 3.7.2'
    return version


def get_node_version():
    # Node is not installed on production API/Python servers
    raw = os.popen('node -v').read().replace('\n', '').strip()
    version = 'Node not installed on this server'
    if len(raw) > 0:
        version = os.popen('node -v').read().replace('\n', '').strip()
    print('Node version: ' + version)    # Something like 'v14.15.1'
    return version


def get_git_merge_date():
    # Assume the latest source file has a timestamp that is the git merge date
    pattern = '""gm'
    list_of_files = [fn for fn in glob.glob('./*/**')
                     if not os.path.basename(fn).endswith(('/', '_')) and
                     re.search(r"/+.*?\..*?$", fn)]  # exclude new directories
    latest_file_string = max(list_of_files, key=os.path.getctime)
    posix_filepath = pathlib.Path(latest_file_string)
    stat_of_file = posix_filepath.stat()
    git_merge_date = str(datetime.datetime.fromtimestamp(stat_of_file.st_mtime)).split('.', 1)[0]
    out_string = git_merge_date + '  (' + latest_file_string + ')'
    # print(out_string)
    return out_string


def get_postgres_version():
    formatted = 'fail'
    try:
        version = str(connection.cursor().connection.server_version)
        version = ' ' + version if len(version) == 5 else version
        formatted = version[0:2] + '.' + version[2:4] + '.' + version[4:6]
    except Exception:
        pass
    print('Postgres version: ', formatted)
    return formatted

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Consider switching to the way that Two Scoops of Django 1.8 suggests file path handling, section 5.6

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_environment_variable("SECRET_KEY")

# Comment out when running Heroku
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1'
]


# Application definition

INSTALLED_APPS = (

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'background_task',
    'bootstrap3',
    'corsheaders',  # cross origin requests
    # 'social.apps.django_app.default',
    'social_django',

    # project specific
    'activity',
    'admin_tools',
    'analytics',
    'api_internal_cache',
    'apis_v1',
    'apple',
    'ballot',
    'bookmark',
    'campaign',
    'candidate',
    'config',
    'donate',
    'elected_office',
    'elected_official',
    'election',
    'electoral_district',
    'email_outbound',
    'exception',
    'follow',
    'friend',
    'geoip',
    'google_custom_search',
    'image',
    'import_export_ballotpedia',
    'import_export_batches',
    'import_export_ctcl',
    'import_export_endorsements',
    'import_export_facebook',
    'import_export_google_civic',
    'import_export_maplight',
    'import_export_twitter',  # See also twitter (below)
    'import_export_vote_smart',
    'import_export_wikipedia',
    'issue',
    'measure',
    'office',
    'organization',
    'party',
    'pledge_to_vote',
    'politician',
    'polling_location',
    'position',
    'quick_info',
    'reaction',
    'rest_framework',    # Jan 2019, looks abandoned
    'retrieve_tables',
    'scheduled_tasks',
    'search',
    'share',
    'sms',
    'stripe_donations',
    'support_oppose_deciding',
    'tag',
    'twitter',  # See also import_export_twitter
    'voter',  # See also AUTH_USER_MODEL in config/settings.py
    'voter_guide',
    'wevote_functions',
    'wevote_settings',
    'wevote_social',
)

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'wevote_social.middleware.SocialMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # Django Cookbook
                'django.template.context_processors.static',  # Django Cookbook
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'wevote_social.context_processors.profile_photo',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = get_environment_variable("TIME_ZONE")

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Described here: https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#a-full-example
AUTH_USER_MODEL = 'voter.Voter'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/ calls loading static files from the project
# "grossly inefficient and probably insecure, so it is unsuitable for production", but we only use it (August 2017) to
# serve apis_v1.css for the admin console.
# If we ever care, there is a better way: https://docs.djangoproject.com/en/1.11/howto/static-files/deployment/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH, "static", "static") if DEBUG else \
    os.path.join(PROJECT_PATH, "apis_v1", "static")  # Django Cookbook
MEDIA_URL = '/media/'  # Django Cookbook
MEDIA_ROOT = os.path.join(PROJECT_PATH, "static", "media")  # Django Cookbook
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'        # Added for Django 3.2, June 2021

# We want to default to cookie storage of messages so we don't overload our app servers with session data
# MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# Default settings described here: http://django-bootstrap3.readthedocs.org/en/latest/settings.html
BOOTSTRAP3 = {

    # The URL to the jQuery JavaScript file
    'jquery_url': '//code.jquery.com/jquery.min.js',

    # The Bootstrap base URL
    'base_url': '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/',

    # The complete URL to the Bootstrap CSS file (None means derive it from base_url)
    'css_url': '//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',

    # The complete URL to the Bootstrap CSS file (None means no theme)
    'theme_url': None,

    # The complete URL to the Bootstrap JavaScript file (None means derive it from base_url)
    'javascript_url': None,

    # Put JavaScript in the HEAD section of the HTML document (only relevant if you use bootstrap3.html)
    'javascript_in_head': False,

    # Include jQuery with Bootstrap JavaScript (affects django-bootstrap3 template tags)
    'include_jquery': False,

    # Label class to use in horizontal forms
    'horizontal_label_class': 'col-md-3',

    # Field class to use in horizontal forms
    'horizontal_field_class': 'col-md-9',

    # Set HTML required attribute on required fields
    'set_required': True,

    # Set HTML disabled attribute on disabled fields
    'set_disabled': False,

    # Set placeholder attributes to label if no placeholder is provided
    'set_placeholder': True,

    # Class to indicate required (better to set this in your Django form)
    'required_css_class': '',

    # Class to indicate error (better to set this in your Django form)
    'error_css_class': 'has-error',

    # Class to indicate success, meaning the field has valid input (better to set this in your Django form)
    'success_css_class': 'has-success',

    # Renderers (only set these if you have studied the source and understand the inner workings)
    'formset_renderers': {
        'default': 'bootstrap3.renderers.FormsetRenderer',
    },
    'form_renderers': {
        'default': 'bootstrap3.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'bootstrap3.renderers.FieldRenderer',
        'inline': 'bootstrap3.renderers.InlineFieldRenderer',
    },
}

CORS_ORIGIN_ALLOW_ALL = True  # CORS_ORIGIN_ALLOW_ALL: if True, the whitelist will not be used & all origins accepted
CORS_ALLOW_CREDENTIALS = True
# specify whether to replace the HTTP_REFERER header if CORS checks pass so that CSRF django middleware checks
# will work with https
CORS_REPLACE_HTTPS_REFERER = True
CSRF_TRUSTED_ORIGINS = ['api.wevoteusa.org']
DATA_UPLOAD_MAX_MEMORY_SIZE = 6000000

# CORS_ORIGIN_WHITELIST = (
#     'google.com',
#     'hostname.example.com'
# )
# CORS_ALLOW_HEADERS = (
#     'access-control-allow-headers',
#     'access-control-allow-methods',
#     'access-control-allow-origin',
#     'x-requested-with',
#     'content-type',
#     'accept',
#     'origin',
#     'authorization',
#     'x-csrftoken',
#     'x-api-key'
# )

SOCIAL_AUTH_FACEBOOK_KEY = get_environment_variable("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = get_environment_variable("SOCIAL_AUTH_FACEBOOK_SECRET")
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']  # , 'user_friends'
SOCIAL_AUTH_TWITTER_KEY = get_environment_variable("SOCIAL_AUTH_TWITTER_KEY")
SOCIAL_AUTH_TWITTER_SECRET = get_environment_variable("SOCIAL_AUTH_TWITTER_SECRET")

SOCIAL_AUTH_LOGIN_ERROR_URL = get_environment_variable("SOCIAL_AUTH_LOGIN_ERROR_URL")
SOCIAL_AUTH_LOGIN_REDIRECT_URL = get_environment_variable("SOCIAL_AUTH_LOGIN_REDIRECT_URL")
SOCIAL_AUTH_LOGIN_URL = get_environment_variable("SOCIAL_AUTH_LOGIN_URL")

LOGIN_REDIRECT_URL = get_environment_variable("LOGIN_REDIRECT_URL")
LOGIN_ERROR_URL = get_environment_variable("LOGIN_ERROR_URL")
LOGIN_URL = get_environment_variable("LOGIN_URL")

SOCIAL_AUTH_URL_NAMESPACE = 'social'

# See description of authentication pipeline:
# https://github.com/omab/python-social-auth/blob/master/docs/pipeline.rst
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    # 'social_core.pipeline.social_auth.social_user',
    'wevote_social.utils.social_user',  # Order in this pipeline matters
    'wevote_social.utils.authenticate_associate_by_email',  # Order in this pipeline matters
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'wevote_social.utils.switch_user'  # Order in this pipeline matters
)

EMAIL_BACKEND = get_environment_variable("EMAIL_BACKEND")
SENDGRID_API_KEY = get_environment_variable("SENDGRID_API_KEY")
# ADMIN_EMAIL_ADDRESSES = get_environment_variable("ADMIN_EMAIL_ADDRESSES")
# # Expecting a space delimited string of emails like "jane@wevote.us" or "jane@wevote.us bill@wevote.us"
# ADMIN_EMAIL_ADDRESSES_ARRAY = []
# if ADMIN_EMAIL_ADDRESSES:
#     # ADMINS is used by lib/python3.6/lib/site-packages/django/core/mail/INIT.py
#     ADMINS = [[email.split('@')[0], email] for email in ADMIN_EMAIL_ADDRESSES.split()]


# ########## Logging configurations ###########
#   LOG_STREAM          Boolean     True will turn on stream handler and write to command line.
#   LOG_FILE            String      Path to file to write to. Make sure executing
#                                   user has permissions.
#   LOG_STREAM_LEVEL    Integer     Log level of stream handler: CRITICAL, ERROR, INFO, WARN, DEBUG
#   LOG_FILE_LEVEL      Integer     Log level of file handler: CRITICAL, ERROR, INFO, WARN, DEBUG
#   NOTE: These should be set in the environment_variables.json file
def convert_logging_level(log_level_text_descriptor):
    import logging
    # Assume error checking has been done and that the string is a valid logging level
    if log_level_text_descriptor == "CRITICAL":
        return logging.CRITICAL
    if log_level_text_descriptor == "ERROR":
        return logging.ERROR
    if log_level_text_descriptor == "INFO":
        return logging.INFO
    if log_level_text_descriptor == "WARN":
        return logging.WARN
    if log_level_text_descriptor == "DEBUG":
        return logging.DEBUG


def lookup_logging_level(log_level_text_descriptor, log_level_default="ERROR"):
    import logging
    available_logging_levels = ["CRITICAL", "ERROR", "INFO", "WARN", "DEBUG"]

    if log_level_text_descriptor.upper() in available_logging_levels:
        # print "log_level_text_descriptor: {}".format(log_level_text_descriptor)
        return convert_logging_level(log_level_text_descriptor)
    else:
        # The log_level_text_descriptor is not a valid level, so use the debug level
        if log_level_default.upper() in available_logging_levels:
            # print "log_level_default: {}".format(log_level_default)
            return convert_logging_level(log_level_default)
        else:
            # print "log_level failure default: {}".format("ERROR")
            return logging.ERROR


# Which level of logging event should get written to the command line?
LOG_STREAM = get_environment_variable('LOG_STREAM')  # Turn command line logging on or off
# print "Current LOG_STREAM_LEVEL setting:"
LOG_STREAM_LEVEL = lookup_logging_level(get_environment_variable("LOG_STREAM_LEVEL"), "DEBUG")
# Which level of logging event should get written to the log file?
LOG_FILE = get_environment_variable('LOG_FILE')  # Location of the log file
LOG_FILE_LEVEL = lookup_logging_level(get_environment_variable("LOG_FILE_LEVEL"), "ERROR")
# print "Current LOG_FILE_LEVEL setting:"

# Using conventions from django.contrib:
# https://docs.djangoproject.com/en/1.8/ref/contrib/gis/geoip/#geoip-settings
GEOIP_PATH = os.path.join(BASE_DIR, 'geoip', 'import_data')
GEOIP_COUNTRY = 'GeoIP.dat'
if os.path.exists(os.path.join(GEOIP_PATH, 'GeoIPCity.dat')):
    GEOIP_CITY = 'GeoIPCity.dat'  # use the paid db
else:
    GEOIP_CITY = 'GeoLiteCity.dat'  # use the free db
