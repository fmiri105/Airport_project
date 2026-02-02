class JWTAuthFromCookieMiddleware:
    """If an 'access_token' cookie exists, copy it into Authorization header for downstream auth.

    This allows DRF's JWTAuthentication to work with browser requests that send the cookie.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If Authorization header not set and cookie present, set the header
        if 'HTTP_AUTHORIZATION' not in request.META:
            token = request.COOKIES.get('access_token')
            if token:
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        response = self.get_response(request)
        return response
