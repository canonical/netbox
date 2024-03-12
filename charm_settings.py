from netbox.original_settings import *
import os
import urllib.parse

MIDDLEWARE.insert(MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')

base_url = os.environ.get('DJANGO_BASE_URL', '/')
parsed_base_url = urllib.parse.urlparse(base_url)

# This is required for Traefik k8s charm to work in routing mode
# path. The reason is that when the proxied url is something like
# http://url/path, the url called by the ingress is really
# http://service/, without the path.  See also
# https://github.com/evansd/whitenoise/issues/271
WHITENOISE_STATIC_PREFIX=STATIC_URL
STATIC_URL = f"{parsed_base_url.path}/{STATIC_URL}"
FORCE_SCRIPT_NAME=f"{parsed_base_url.path}"
MEDIA_URL = f"{parsed_base_url.path}/{MEDIA_URL}"
