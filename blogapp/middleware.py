from django.http import HttpResponseRedirect

class HttpsToHttpRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is an HTTPS request
        if request.is_secure():
            # Redirect to HTTP version of the same URL
            url = request.build_absolute_uri(request.get_full_path())
            url = url.replace('https://', 'http://')
            return HttpResponseRedirect(url)
            
        # Process the response
        response = self.get_response(request)
        return response

    def process_request(self, request):
        # Check if this is an HTTPS request
        if request.is_secure():
            # Redirect to HTTP version of the same URL
            url = request.build_absolute_uri(request.get_full_path())
            url = url.replace('https://', 'http://')
            return HttpResponseRedirect(url)
        
        return None 