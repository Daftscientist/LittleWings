from functools import wraps
from sanic import response
from database import key_valid

def protected_route():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            # Check if the request has a valid API key
            if "Authorization" not in request.headers:
                return response.json({"error": "No API key provided"}, 401)
            api_key = request.headers["Authorization"]
            # Check if the API key is valid
            if not api_key.startswith("Bearer "):
                return response.json({"error": "Invalid API key format"}, 401)
            if not await key_valid(api_key):
                return response.json({"error": "Invalid API key"}, 401)
            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator