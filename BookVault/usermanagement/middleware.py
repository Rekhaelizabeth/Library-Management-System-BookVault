from django.shortcuts import redirect

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure resolver_match is not None
        if request.resolver_match is not None:
            if request.user.is_authenticated:
                allowed_roles = getattr(request.resolver_match.func, 'allowed_roles', None)
                if allowed_roles and request.user.role not in allowed_roles:
                    return redirect('access_denied')  # Replace with your custom access-denied page URL name
        return self.get_response(request)
