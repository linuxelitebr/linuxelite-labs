#!/usr/bin/env python3
"""The ECB penguin, generated for real.

Draws a simple penguin (large flat regions), then encrypts the raw pixels with
AES-256 twice: once in ECB and once in CTR. Same key, same algorithm, same
image. The only thing that changes is the mode.

ECB encrypts each 16-byte block independently, so identical plaintext blocks
(the flat regions) become identical ciphertext blocks, and the outline of the
penguin survives the encryption. CTR (a stream mode) turns the same image into
noise, which is what "encrypted" is supposed to look like.

That is the whole point: picking AES is not enough. The mode decides whether it
protects anything.
"""
import os
from PIL import Image, ImageDraw
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SIZE = 256  # 256x256, grayscale -> 65536 bytes, a clean multiple of 16
HERE = os.path.dirname(os.path.abspath(__file__))


def draw_penguin():
    """A blocky penguin with big flat regions, in grayscale."""
    img = Image.new("L", (SIZE, SIZE), 235)
    d = ImageDraw.Draw(img)
    d.ellipse([64, 36, 192, 232], fill=28)     # body
    d.ellipse([92, 92, 164, 224], fill=250)    # belly
    d.ellipse([98, 66, 122, 96], fill=250)     # eye whites
    d.ellipse([134, 66, 158, 96], fill=250)
    d.ellipse([106, 74, 116, 88], fill=20)     # pupils
    d.ellipse([142, 74, 152, 88], fill=20)
    d.polygon([(120, 92), (140, 92), (130, 110)], fill=150)  # beak
    d.ellipse([80, 214, 120, 238], fill=150)   # feet
    d.ellipse([136, 214, 176, 238], fill=150)
    return img


def aes_ecb(data, key):
    enc = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return enc.update(data) + enc.finalize()


def aes_ctr(data, key):
    enc = Cipher(algorithms.AES(key), modes.CTR(os.urandom(16))).encryptor()
    return enc.update(data) + enc.finalize()


def main():
    key = os.urandom(32)  # AES-256, the same key for both modes
    penguin = draw_penguin()
    raw = penguin.tobytes()
    assert len(raw) % 16 == 0, "image bytes must be a multiple of the AES block"

    penguin.save(os.path.join(HERE, "penguin-original.png"))
    Image.frombytes("L", (SIZE, SIZE), aes_ecb(raw, key)).save(
        os.path.join(HERE, "penguin-ecb.png"))
    Image.frombytes("L", (SIZE, SIZE), aes_ctr(raw, key)).save(
        os.path.join(HERE, "penguin-secure.png"))

    print("wrote penguin-original.png, penguin-ecb.png, penguin-secure.png")
    print("same AES-256 key both ways; only the mode differs.")
    print("ECB keeps the penguin visible. CTR does not. That is the mode talking.")


if __name__ == "__main__":
    main()
