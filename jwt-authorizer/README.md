# jwt-authorizer

Validate a JWT without an AWS account, the way an API Gateway / Cognito
authorizer should.

Companion to the post *Autenticacao no Amazon API Gateway com Cognito e JWT*.

## Run it

```bash
pip install -r requirements.txt
python demo.py
```

It generates an RSA key, mints an RS256 JWT the way Cognito does, builds the
matching JWKS, and validates it three ways:

- a valid token is accepted;
- a token with an edited payload is rejected (`InvalidSignatureError`): the
  signature no longer fits the changed payload;
- an `alg: none` token is rejected (`InvalidAlgorithmError`): the algorithm is
  pinned to RS256, so the classic "just set alg to none" bypass fails.

## The point

Decoding a JWT is trivial: the header and payload are base64url, readable by
anyone. The signature is the only thing that proves the token is real and
unedited. So an authorizer must pin the algorithm, verify the signature against
the issuer's JWKS, and then check the claims (`iss`, `token_use`,
`client_id`/`aud`, `exp`). Skip the signature check and you are trusting a badge
anyone can print at home.
