from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTScheme(OpenApiAuthenticationExtension):
    target_class = JWTAuthentication
    name = 'Bearer Auth'
    
    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Enter your JWT token in the format: Bearer <token>'
        }