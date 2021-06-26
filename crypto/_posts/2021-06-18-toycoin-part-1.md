---
layout: post
title:  "Toycoin Part 1: Crypto Basics"
date:   2021-06-18 14:00:00 -0500
tags:   python blockchain
---

**Note: the `toycoin` series of posts is for learning / illustrative purposes only; no part of it should be considered secure or useful for real-world purposes.**

As I started to learn a bit about blockchain technology recently, I decided to try a toy blockchain implementation (in Python), ideally with some visualizations of network activity (in Elm).

As with so many things, the theory is very interesting, but the details of implementation require deeper thought. Since this is a learning exercise, I'm mostly trying to read just the basic theories and independently come up with something minimal that "works", rather then copying too much from reference implementations.


## Crypto

The `pycrypto` library has been deprecated for a while, with `pycryptodome` and `cryptography` as alternatives recommended by the community. I chose [`cryptography`](https://cryptography.io/en/latest/) as it seems to emphasize a sound approach to cryptography (don't do it yourself!), but implementation correctness / security is not so much a concern for this learning exercise.

### Hashing

Hasning is a primitive that's required for blockchain operations.

Wrapping the library `hash` function with a default algorithm of SHA-512:

```python
from cryptography.hazmat.primitives import hashes # typing: ignore


Digest = bytes


def hash(msg: bytes, algo = hashes.SHA512()) -> Digest:
    """Hash given msg."""
    digest = hashes.Hash(algo)
    digest.update(msg)
    return digest.finalize()
```

This works as expected (verified against an independent online source and added as a test case):

```python
In [1]: from toycoin import hash

In [2]: hash.hash(b'hello world').hex()
Out[2]: '309ecc489c12d6eb4cc40f50c902f2b4d0ed77ee511a7c7a9bcd3ca86d4cd86f989dd35bc5ff499670da34255b45b0cfd830e81f605dcf7dc5542e93ae9cd76f'

```


### Digital Signatures

RSA keys can be used ot sign and verify messages (or more specifically, in Nakamoto's Bitcoin paper, transactions from one Bitcoin owner to another).

Following [the docs](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/?highlight=rsa#module-cryptography.hazmat.primitives.asymmetric.rsa):

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


Signature = bytes


def gen_priv_key(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """Generate RSA key with modulus of given size in bits."""
    return rsa.generate_private_key(public_exponent=65537, key_size=key_size)


def get_pub_key(priv_key: rsa.RSAPrivateKey) -> rsa.RSAPublicKey:
    """Get RSA pubic key from private key."""
    return priv_key.public_key()
```

Next, again following [the docs](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/?highlight=sign#signing), we specify signing and verifying messages. The library recommendation is to use PSS as the padding sheme, and we hard code SHA512 as the hashing algorithm.

```python

HASH = hashes.SHA512()

PADDING = padding.PSS(mgf=padding.MGF1(HASH),
                      salt_length=padding.PSS.MAX_LENGTH)


def sign(priv_key: rsa.RSAPrivateKey, msg: bytes) -> Signature:
    """Sign msg with RSA private key."""
    return priv_key.sign(msg, PADDING, HASH)


def verify(signature: Signature, pub_key: rsa.RSAPublicKey, msg: bytes) -> bool:
    """Verify msg signature with RSA public key."""
    try:
        pub_key.verify(signature, msg, PADDING, HASH)
    except:
        return False
    return True
```

The default behavior for `verify` is to raise an exception, so we just wrap that into a boolean check instead (a bit more functional maybe). We can write a test case to verify that the round trip (signing and verifying) works:


```python
def test_roundtrip(self):
    """Test sign and verify."""

    msg = b'hello world'

    priv_key = signature.gen_priv_key()
    pub_key = signature.get_pub_key(priv_

    s = signature.sign(priv_key, msg)

    assert signature.verify(s, pub_key, msg) is True
    assert signature.verify(s[:-1], pub_key, msg) is False
    assert signature.verify(s, pub_key, msg[:-1]) is False
```

Note that all test cases for `toycoin` are written for `pytest`.



## Wrapping Up

This was mostly just lightly wrapping `cryptography` functions, but it was helpful to read the docs a bit and work out the type signatures.

[Code on Github](https://github.com/tkuriyama/toycoin/tree/master/blockchain/toycoin)

### References

- [Nakamoto Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf)
