import time
from collections import defaultdict
from django.http import JsonResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Store IP request history in-memory: ip -> list of floats (timestamps)
        self.request_history = defaultdict(list)
        self.rate_limit = 60  # max 10 requests
        self.time_window = 60  # per 60 seconds (1 minute)

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')

        now = time.time()
        
        # Filter timestamps to keep only those within the active 60-second window
        timestamps = self.request_history[ip]
        self.request_history[ip] = [t for t in timestamps if now - t < self.time_window]
        
        # Enforce rate limit
        if len(self.request_history[ip]) >= self.rate_limit:
            return JsonResponse(
                {"detail": "Too many requests. Limit is 10 requests per minute."},
                status=429
            )
            
        # Log the timestamp of the new request
        self.request_history[ip].append(now)
        
        return self.get_response(request)
