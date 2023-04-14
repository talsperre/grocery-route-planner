import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Kayak, deed, rotator, noon, race car'
    TEMPLATES_AUTO_RELOAD = True
