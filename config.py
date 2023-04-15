import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Kayak, deed, rotator, noon, race car'
    GMAPS_API_SECRET_KEY = os.environ.get('gmaps_key', "No key found")
    TEMPLATES_AUTO_RELOAD = True
