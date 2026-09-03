#!/usr/bin/env python3
"""AES-256-GCM done right, and the one way to break it.

Three things:
1. A correct encrypt/decrypt round trip with a fresh nonce.
2. Tamper detection: flip one bit of the ciphertext and decryption refuses it.
3. The catastrophe: reuse a nonce under the same key, XOR the two ciphertexts,
   and the keystream cancels out, handing the attacker P1 xor P2 with no key.
   That is why NIST says nonce uniqueness is "almost as important as the
   secrecy of the key."
"""
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def main():
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)

    # 1. Correct usage: a fresh 96-bit nonce per message.
    nonce = os.urandom(12)
    aad = b"non-secret-but-authenticated-header"
    ct = aesgcm.encrypt(nonce, b"transfer: 1000 to account 42", aad)
    pt = aesgcm.decrypt(nonce, ct, aad)
    print("[ok] round trip:", pt.decode())

    # 2. Tamper detection: one flipped bit and decrypt raises InvalidTag.
    tampered = bytearray(ct)
    tampered[0] ^= 0x01
    try:
        aesgcm.decrypt(nonce, bytes(tampered), aad)
        print("[!!] tamper NOT detected (should never happen)")
    except Exception as e:
        print("[ok] tamper rejected:", type(e).__name__)

    # 3. The catastrophe: the SAME nonce for two messages under the same key.
    bad_nonce = os.urandom(12)
    m1 = b"attack at dawn!!"
    m2 = b"retreat at noon!"
    c1 = aesgcm.encrypt(bad_nonce, m1, None)
    c2 = aesgcm.encrypt(bad_nonce, m2, None)
    # Strip the 16-byte tag and XOR the ciphertexts.
    xor_ct = bytes(a ^ b for a, b in zip(c1[:-16], c2[:-16]))
    xor_pt = bytes(a ^ b for a, b in zip(m1, m2))
    print("[reuse] C1 xor C2 == P1 xor P2 :", xor_ct == xor_pt)
    print("        the keystream cancels; the attacker gets P1 xor P2 with no key,")
    print("        and a repeated nonce also leaks the GHASH key, enabling forgeries.")


if __name__ == "__main__":
    main()
