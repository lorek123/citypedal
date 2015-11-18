from .settings import *

# INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True
}

XSS_PROTECT = 'on'
