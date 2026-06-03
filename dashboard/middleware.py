from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
import time


class RollingSessionMiddleware:
    """
    Enforces a rolling 15-minute inactivity logout window.
    Every authenticated request resets the session expiry.
    API endpoints (JWT-authenticated) are excluded.
    """

    EXEMPT_PATHS = ['/api/', '/login/', '/admin/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not self._is_exempt(request.path):
            last_activity = request.session.get('last_activity')
            now = time.time()
            timeout = getattr(settings, 'SESSION_COOKIE_AGE', 900)

            if last_activity and (now - last_activity) > timeout:
                from django.contrib.auth import logout
                logout(request)
                return redirect(f"{settings.LOGIN_URL}?next={request.path}&timeout=1")

            request.session['last_activity'] = now

        response = self.get_response(request)
        return response

    def _is_exempt(self, path):
        return any(path.startswith(p) for p in self.EXEMPT_PATHS)
