import threading
from django.utils.deprecation import MiddlewareMixin
from core.models import School

# This creates a safe, isolated memory space for the current web request
_thread_locals = threading.local()


def get_current_school():
    """Helper function to grab the school from anywhere in the app."""
    return getattr(_thread_locals, "school", None)


class TenantMiddleware(MiddlewareMixin):
    """
    Intercepts every API request.
    For now, it forces the tenant to be 'kaliyar'.
    Later, it will look at the user's JWT token to figure out their school.
    """

    def process_request(self, request):
        # HARDCODED FOR NOW: Until we build Auth, pretend everyone is from Kaliyar
        school = School.objects.filter(tenant_code="kaliyar").first()

        # Attach the school to the current thread AND the request object
        _thread_locals.school = school
        request.school = school

    def process_response(self, request, response):
        # Clean up memory after the request is done
        if hasattr(_thread_locals, "school"):
            del _thread_locals.school
        return response
