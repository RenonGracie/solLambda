from flask_openapi3 import Info, OpenAPI

from src.utils.logger import init_logger

__jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
__security_schemes = {"jwt": __jwt}

info = Info(title="SolHealth API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=__security_schemes)
app.json.sort_keys = False

# Setup logging
logger = init_logger(app)
