---
layout: post
title:  "Toycoin Part 3: Transactions"
date:   2021-06-30 07:00:00 -0500
tags:   python blockchain
---


**Note: the toycoin series of posts is for learning / illustrative purposes only; no part of it should be considered secure or useful for real-world purposes.**

Transactions are the raison d'être of the original blockchain. Described in Section of [Nakamoto's whitepaper](https://bitcoin.org/bitcoin.pdf), a transaction is simply a transfer of coin from one owner to the next. (And the whole point of the blockchain being the mechanism to check that such transactions are valid and the coins are not being double-spent, without relying on a central authority.)


## Data Model

We could consider modeling a simple transaction as follows, with what seems like the minimally required fields:

```python
Address = bytes

class Transaction(TypedDict):
    sender: Address
    receiver: Address
    amount: float
    signature: signature.Signature
```

It turns out that `sender` is not required explicitly, since each transaction is signed by the sender. Omitting it saves space, and maybe there's something philosophically aligned with the anonymours nature of the blockchain (even though, technically, all transactions are public and forever traceable to original owners). So we have:

```python
class Transaction(TypedDict):
    receiver: Address
    amount: float
    signature: signature.Signature
```


## Transactions

Generating a transaction (sending coins) is a direct construction of the `TypedDict` specified above:

```python
def send(receiver: bytes,
         sender: rsa.RSAPrivateKey,
         amount: float,
         previous_txn: Transaction
         ) -> Transaction:
    """Generate a new transaction."""
    h = hash_txn(previous_txn)
    return {'receiver': receiver,
            'amount': amount,
            'signature': signature.sign(sender, h + receiver)}
```

Note that the construction of a valid transaction requires a prior construction. Presumably, there is a special genesis transaction in blockchains, just as there is a genesis block. (For testing purposes, any signature can be used for the signature of the genesis transaction, since it doesn't need to be verified (probably?)).

The constructions requires a `hash_transaction` function:

```python
def hash_txn(txn: Transaction) -> Hash:
    """Hash Transaction."""
    return hash.hash(txn['receiver'] +
                     bytes(str(txn['amount']).encode('utf-8')) +
                     txn['signature'])

```

... which seems like a reasonable way to do it, but could be terribly insecure! (Also, it feels like htere should be a better way to hash floats than hashing the string represetation?)

Validation is essentially just checking the signature (see [Part 1](https://tkuriyama.github.io/crypto/2021/06/18/toycoin-part-1.html) of this series). `valid` operates on a list or transactions and returns `None` if the list is too short -- since no validation can be performed without a prior transaction. 

```python
def valid(txns: List[Transaction]) -> Optional[bool]:
    """Verify signatures of a list of transactions."""
    if len(txns) <= 1:
        return None

    pairs = zip(txns, txns[1:])
    return all(valid_pair(prev, this) for prev, this in pairs)


def valid_pair(previous: Transaction, this: Transaction) -> bool:
    """Verify signature of one transaction."""
    return signature.verify(this['signature'],
                            signature.load_pub_key_bytes(previous['receiver']),
                            hash_txn(previous) + this['receiver'])


```

## Example

Let's generate some RSA keys and a genesis transaction...

```python
In [102]: a_priv, b_priv = signature.gen_priv_key(), signature.gen_priv_key()

In [103]: c_priv, d_priv = signature.gen_priv_key(), signature.gen_priv_key()

In [104]: txn0 = {'receiver': signature.get_pub_key_bytes(a_priv),
     ...:        'amount': 100.0,
     ...:        'signature': b'genesis_signature'
     ...:        }
```

Now we call the `send` interface:

```python
In [105]: txn1 = transaction.send(signature.get_pub_key_bytes(b_priv),
     ...:                         a_priv,
     ...:                         99.0,
     ...:                         txn0)
     ...: txn2 = transaction.send(signature.get_pub_key_bytes(c_priv),
     ...:                         b_priv,
     ...:                         99.0,
     ...:                         txn1)

```

And finally, testing `valid` on the chain of transactions:

```python
In [107]: transaction.valid([txn0, txn1, txn2])
Out[107]: True

In [108]: transaction.valid([txn0, txn2, txn1])
Out[108]: False
```


## Tests

[Tests](https://github.com/tkuriyama/toycoin/blob/master/blockchain/tests/test_transaction.py) codify an example like the above, with a few more edge cases.


## Wrapping Up

As usual, even with very simple modules, there is quite a bit of detail that leads to questions and design decisions. 

It's still unclear to me how transactions are handled by the network. e.g.: 

- do blockahin users send transactions to full nodes for construction and broadcasting, since presumably there will be a lot more users of the blockchain compared to maintainers? 
- what does it mean for a payee to verify signatures, if they're just a user and not a full node?
- what if two valid transactions are received in different order by different full codes?

But presumably those are all questions for the network protocol and orthogonal to this post. ALso, we've kept transcations so simple that they can easily be modified as necessary. 


[Code on Github](https://github.com/tkuriyama/toycoin/tree/master/blockchain/toycoin)


## References

- [Nakamoto Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf)

