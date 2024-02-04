from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Globally set the rate limit for all routes in the application to 50 per 5 minutes
limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["50 per 5 minutes"]
    )


