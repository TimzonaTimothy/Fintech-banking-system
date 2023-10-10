from django.http import HttpResponseServerError
from django.conf import settings
import os

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if os.path.exists(settings.MAINTENANCE_FILE):
            # If the maintenance file exists, serve its content as the response
            with open(settings.MAINTENANCE_FILE, 'r') as maintenance_file:
                maintenance_content = maintenance_file.read()
            response = HttpResponseServerError(content_type='text/html')
            response.content = maintenance_content
            return response

        response = self.get_response(request)
        return response