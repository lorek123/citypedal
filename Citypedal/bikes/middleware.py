from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from re import compile

EXEMPT_URLS = [compile(reverse('login').lstrip('/')),
               compile(settings.MEDIA_URL.lstrip('/'))]


class LoginRequiredMiddleware:

    def process_request(self, request):
        if not request.user.is_authenticated():
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(reverse('login'))
