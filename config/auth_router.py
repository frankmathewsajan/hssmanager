from ninja import Router
from ninja.schema import Schema
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken

auth_router = Router(tags=["Authentication"])


# The IN schema (What Next.js sends us)
class LoginRequest(Schema):
    username: str
    password: str


# The OUT schema (What we send back to Next.js)
class LoginResponse(Schema):
    token: str
    name: str
    role: str
    school_code: str


@auth_router.post("/login", response={200: LoginResponse, 401: dict})
def login(request, payload: LoginRequest):
    """Verifies credentials and issues a JWT token for Next.js."""
    user = authenticate(username=payload.username, password=payload.password)

    if user and hasattr(user, "employee_profile"):
        emp = user.employee_profile

        # Generate the JWT Token
        refresh = RefreshToken.for_user(user)

        return 200, {
            "token": str(refresh.access_token),
            "name": emp.name,
            "role": emp.designation.name,  # e.g., 'Principal' or 'HSST'
            "school_code": emp.school.tenant_code if emp.school else "system",
        }

    return 401, {"detail": "Invalid username or password"}
