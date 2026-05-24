from ninja import Router
from ninja.schema import Schema
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.schema import TokenRefreshInputSchema

auth_router = Router(tags=["Authentication"])


# The IN schema (What Next.js sends us)
class LoginRequest(Schema):
    username: str
    password: str
    remember_me: bool = (
        False  # Optional field to indicate if the user wants to be remembered
    )


# The OUT schema (What we send back to Next.js)
class LoginResponse(Schema):
    token: str
    refresh_token: str
    name: str
    role: str
    school_code: str


@auth_router.post("/login", response={200: LoginResponse, 401: dict})
def login(request, payload: LoginRequest):
    """Verifies credentials and issues a JWT token for Next.js."""
    user = authenticate(username=payload.username, password=payload.password)

    if user and hasattr(user, "employee_profile"):
        emp = user.employee_profile
        refresh = RefreshToken.for_user(user)

        refresh["role"] = emp.designation.name
        refresh["school_code"] = emp.school.tenant_code if emp.school else "99999"

        return 200, {
            "token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "name": emp.name,
            "role": emp.designation.name,  # e.g., 'Principal' or 'HSST'
            "school_code": emp.school.tenant_code if emp.school else "99999",
        }

    return 401, {"detail": "Invalid username or password"}


class RefreshRequest(Schema):
    refresh: str


class RefreshResponse(Schema):
    access: str


@auth_router.post("/refresh", response={200: RefreshResponse, 401: dict})
def refresh_token(request, payload: RefreshRequest):
    """Refreshes the JWT token."""
    try:
        refresh = RefreshToken(payload.refresh)
        return 200, {"access": str(refresh.access_token)}
    except Exception as e:
        return 401, {"detail": "Invalid or expired refresh token"}
