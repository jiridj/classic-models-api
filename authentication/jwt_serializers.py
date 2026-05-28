from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from .jwt_tokens import CustomRefreshToken, get_jwt_kid


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Refresh serializer that ensures the returned access token carries a `kid` JOSE header.
    """

    token_class = CustomRefreshToken

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        kid = get_jwt_kid()
        if kid:
            refresh.headers["kid"] = kid
            access = refresh.access_token
            access.headers["kid"] = kid
            data["access"] = str(access)

        return data

