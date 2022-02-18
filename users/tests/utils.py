from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Profile


def _create_token(profile: Profile) -> str:
    """Create a new, valid access token for the given profile."""
    return RefreshToken.for_user(profile.user).access_token


def _create_profile(profile_data: dict, password: str) -> Profile:
    """Create a new profile with the given data and user password."""
    data = profile_data.copy()
    user = get_user_model().objects.create()
    user.set_password(password)
    user.save(update_fields=["password"])
    profile = Profile.objects.create(user=user, **data)
    profile.refresh_from_db()
    return profile


def assert_profile_match_data(profile: Profile, data: dict):
    for field in (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "street_address",
        "city",
        "postal_code",
        "contact_language",
        "national_identification_number",
    ):
        if field in data:
            assert data[field] == str(getattr(profile, field))
