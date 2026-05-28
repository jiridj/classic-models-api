import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey


def _b64url_uint(val: int) -> str:
    if val < 0:
        raise ValueError("uint must be non-negative")
    byte_length = max(1, (val.bit_length() + 7) // 8)
    data = val.to_bytes(byte_length, "big")
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def load_rsa_public_key(pem: str) -> RSAPublicKey:
    key = serialization.load_pem_public_key(pem.encode("utf-8"))
    if not isinstance(key, RSAPublicKey):
        raise TypeError("JWT_PUBLIC_KEY_PEM must be an RSA public key (PEM)")
    return key


@dataclass(frozen=True)
class JwkRsaPublic:
    kid: str
    n: str
    e: str

    def as_dict(self) -> dict:
        return {
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": self.kid,
            "n": self.n,
            "e": self.e,
        }


def jwk_from_public_key_pem(public_pem: str, *, kid: Optional[str] = None) -> JwkRsaPublic:
    key = load_rsa_public_key(public_pem)
    numbers = key.public_numbers()

    n = _b64url_uint(numbers.n)
    e = _b64url_uint(numbers.e)

    if not kid:
        # RFC 7638 JWK Thumbprint (SHA-256) over the required members.
        thumbprint_obj = {"e": e, "kty": "RSA", "n": n}
        thumbprint_json = json.dumps(
            thumbprint_obj, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
        digest = hashlib.sha256(thumbprint_json).digest()
        kid = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

    return JwkRsaPublic(kid=kid, n=n, e=e)

