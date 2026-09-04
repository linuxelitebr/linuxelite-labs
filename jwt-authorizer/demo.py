#!/usr/bin/env python3
"""Validate a JWT the way an API Gateway / Cognito authorizer should, no AWS.

Generates an RSA key, mints an RS256 JWT the way Cognito does, builds the
matching JWKS, and validates it three ways:
  1. a good token passes,
  2. a token with an edited payload is rejected (the signature no longer fits),
  3. an alg:none token is rejected (the algorithm is pinned to RS256).

The whole point of the post, in code: decoding a JWT is trivial, but only the
signature proves it is real. Pin the algorithm, verify the signature, then
check the claims.
"""
import base64
import json
import time

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

ISSUER = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_demo"
CLIENT_ID = "demo-app-client"
KID = "demo-key-1"


def b64url_decode(seg):
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def b64url_encode(obj):
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()


def jwks_of(public_key):
    """What Cognito publishes at /.well-known/jwks.json."""
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public_key))
    jwk.update({"kid": KID, "use": "sig", "alg": "RS256"})
    return {"keys": [jwk]}


def mint(private_key):
    claims = {
        "sub": "user-42",
        "iss": ISSUER,
        "client_id": CLIENT_ID,
        "token_use": "access",
        "scope": "api/read",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": KID})


def validate(token, public_key):
    """The checks, none optional. Raises on any failure."""
    claims = jwt.decode(token, public_key, algorithms=["RS256"], issuer=ISSUER)
    if claims.get("token_use") != "access":
        raise jwt.InvalidTokenError("wrong token_use")
    if claims.get("client_id") != CLIENT_ID:
        raise jwt.InvalidTokenError("wrong client_id")
    return claims


def tamper(token):
    """An attacker edits the payload (sub -> admin) and keeps the old signature."""
    header_b64, payload_b64, sig_b64 = token.split(".")
    payload = json.loads(b64url_decode(payload_b64))
    payload["sub"] = "admin"
    return f"{header_b64}.{b64url_encode(payload)}.{sig_b64}"


def alg_none(token):
    """A token that claims 'alg': none and carries no signature at all."""
    payload = json.loads(b64url_decode(token.split(".")[1]))
    return f"{b64url_encode({'alg': 'none', 'kid': KID})}.{b64url_encode(payload)}."


def main():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    print("JWKS the authorizer would fetch (truncated):")
    print(json.dumps(jwks_of(public_key))[:120] + " ...\n")

    token = mint(private_key)

    claims = validate(token, public_key)
    print("[ok]   valid token accepted. sub =", claims["sub"], "| scope =", claims["scope"])

    try:
        validate(tamper(token), public_key)
        print("[!!]   tampered token ACCEPTED (should never happen)")
    except jwt.PyJWTError as e:
        print("[ok]   tampered token rejected:", type(e).__name__)

    try:
        validate(alg_none(token), public_key)
        print("[!!]   alg:none token ACCEPTED (should never happen)")
    except jwt.PyJWTError as e:
        print("[ok]   alg:none token rejected:", type(e).__name__)


if __name__ == "__main__":
    main()
