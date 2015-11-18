from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from re import compile

EXEMPT_URLS = [compile(reverse('two_factor:login').lstrip('/')),
               compile(settings.MEDIA_URL.lstrip('/'))]


class LoginRequiredMiddleware:

    def process_request(self, request):
        if not request.user.is_authenticated():
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(reverse('login'))


class TwoFARequiredMiddleware:
    """
    Enforce 2FA on registered users.
    """

    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_verified():

            path = request.path_info.rstrip('/')
            otp_init = reverse('two_factor:profile')
            if not path.startswith(otp_init.rstrip('/')):
                return HttpResponseRedirect(otp_init)
