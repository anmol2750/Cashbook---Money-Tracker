from django.utils import translation


class UserLanguageMiddleware:
    """Apply the signed-in user's saved language preference to each request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            language = request.user.language
            request.LANGUAGE_CODE = language
            with translation.override(language):
                response = self.get_response(request)
            # LocaleMiddleware reads the active language when setting response headers.
            translation.activate(language)
            return response
        return self.get_response(request)
