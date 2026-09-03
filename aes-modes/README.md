# aes-modes

Two small proofs that with AES the mode matters as much as the algorithm.

Companion to the post *AES vs DES vs 3DES: qual usar, e por que o modo importa
tanto quanto o algoritmo*. Everything here uses real AES-256 from the `cryptography`
library, no toy ciphers.

## Setup

```bash
pip install -r requirements.txt
```

## The ECB penguin, generated for real

```bash
python ecb_penguin.py
```

Draws a penguin, then encrypts its raw pixels with AES-256 twice with the same
key: once in ECB, once in CTR. It writes three files:

- `penguin-original.png` - the plaintext image.
- `penguin-ecb.png` - AES-256 in ECB mode. The penguin is still there. ECB
  encrypts each 16-byte block independently, so the flat regions (identical
  input blocks) become identical ciphertext blocks and the outline survives.
- `penguin-secure.png` - AES-256 in CTR mode. Noise, which is what encrypted is
  supposed to look like.

Same key, same algorithm, same image. Only the mode changed. That is the whole
argument for never using ECB.

## AES-256-GCM, done right and broken once

```bash
python gcm_demo.py
```

Shows three things: a correct encrypt/decrypt round trip with a fresh nonce;
tamper detection (flip one bit and `decrypt` raises `InvalidTag`); and the
catastrophe of reusing a nonce under the same key. Reuse the nonce, XOR the two
ciphertexts, and the keystream cancels: you recover `P1 xor P2` with no key. A
repeated nonce also leaks the GHASH authentication key, which enables forgeries.
NIST puts nonce uniqueness "almost as important as the secrecy of the key," and
this is why.

## The takeaway

DES is broken, 3DES was retired by NIST, AES is the standard. But AES with the
wrong mode protects nothing. Use AES-256-GCM, give every message a unique nonce,
and never use ECB.
