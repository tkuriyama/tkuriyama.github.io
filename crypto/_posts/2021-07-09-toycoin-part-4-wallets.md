---
layout: post
title:  "Toycoin Part 4: Wallets"
date:   2021-07-09 09:00:00 -0500
tags:   python blockchain
---

**Note: the toycoin series of posts is for learning / illustrative purposes only; no part of it should be considered secure or useful for real-world purposes.**

The [previous post](https://tkuriyama.github.io/crypto/2021/07/09/toycoin-part-3b-transactions-revised.html) described transactions and tokens.

Clients that store tokens and interact with the blockchain via transactions are wallets.
We can imagine the simplest wallet as storing its address (public key), its private key for signing transactions, and the tokens that it holds.

```python
class Wallet:
    """Wallet, initialized with owner's RSA keys."""


    def __init__(self,
                 public_key: bytes,
                 private_key: rsa.RSAPrivateKey):
        self.wallet : List[transaction.Token] = []
        self.pending : List[Tuple[bytes, transaction.Token]] = []
        self.public_key = public_key
        self.private_key = private_key


    def balance(self) -> int:
        """Return current wallet balance (exclude pending)."""
        return sum(token['value'] for token in self.wallet)
```

Wallets submit transactions to the network when they want to send tokens to other wallets. Since the blockchain protocotol needs to confirm the transactions (by including them in blocks), the wallet includes a `pending` store. 


Sending is a matter of finding enough tokens and calling the `send` interface defined in `transactions`. For now, the actual sending -- the networking component -- is ignored. 

```python`
    def send(self,
             send_value: int,
             receiver: bytes
             ) -> Optional[Tuple[List[transaction.Token],
                                 transaction.Transaction]]:
        """Attempt to generate transaction that sends value.
        Tokens included in the transaction are placed in pending state.
        """
        if send_value > self.balance():
            return None

        # FIFO
        sum_value, i = 0, 0
        while sum_value < send_value:
            sum_value += self.wallet[i]['value']
            i += 1

        tokens, txn = transaction.send(receiver,
                                       self.public_key,
                                       self.private_key,
                                       send_value,
                                       self.wallet[:i])

        self.pending.append((transaction.hash_txn(txn), self.wallet[:i]))
        self.wallet = self.wallet[i:]

        return tokens, txn
```

Since `send` places tokens in the `pending` store, we can imagine that network messages will trigger some sort of resolution:

```python

    def confirm_send(self, txn_hash: bytes):
        """Remove confirmed transaction from pending state."""
        self.pending = [(h, tokens) for h, tokens in self.pending
                        if h != txn_hash]


    def reject_send(self, txn_hash: bytes):
        """Return tokens to wallet from pending state."""
        pending = []
        for h, tokens in self.pending:
            if h == txn_hash:
                self.wallet = tokens + self.wallet
            else:
                pending.append((h, tokens))
        self.pending = pending
```

There is some iterating required, if we imagine that multiple transacitons may be pending at any given time.

As for receiving tokens, we merely need to check if we are receiving tokens from another wallet, or from ourselves (in the case of getting change back).

```python
    def receive(self, txn: transaction.Transaction):
        """Add tokens to wallet."""
        if txn is None:
            return

        txn_hash = transaction.hash_txn(txn)
        if self.public_key == txn['receiver']:
            self.wallet.append({'txn_hash': txn_hash,
                                'owner': self.public_key,
                                'value': txn['receiver_value'],
                                'signature': txn['receiver_signature']})
        elif self.public_key == txn['sender']:
            self.wallet.append({'txn_hash': txn_hash,
                                'owner': self.public_key,
                                'value': txn['sender_change'],
```

Note that no logic for validating the received transactions is included. It's assumed that the network will only broadcast validated transactions (e.g. as completed blocks). Additionally, wallets can include additional functionality to request the Merkle hash paths for transactions in prior blocks -- to be addressed later.



## Testing

We can set up some wallets and genesis transactions, and test the wallet and transaction modules together.

```python
    def test_send_receive(self):
        """Test sending and receiving tokens via transactions."""
        a_wallet, b_wallet = gen_wallet(), gen_wallet()
        c_wallet, d_wallet = gen_wallet(), gen_wallet()

        txn0a = {'previous_hashes': [],
                 'receiver': a_wallet.public_key,
                 'receiver_value': 100,
                 'receiver_signature': b'',
                 'sender': b'genesis',
                 'sender_change': 0,
                 'sender_signature': b''
                 }
        txn0b = {'previous_hashes': [],
                 'receiver': a_wallet.public_key,
                 'receiver_value': 50,
                 'receiver_signature': b'',
                 'sender': b'genesis',
                 'sender_change': 0,
                 'sender_signature': b''
                 }

        # genesis receive (the genesis txn is not valid)
        assert transaction.valid_txn([], txn0a) is False
        assert transaction.valid_txn([], txn0b) is False

        assert a_wallet.balance() == 0
        a_wallet.receive(txn0a)
        assert a_wallet.balance() == 100

        a_wallet.receive(txn0b)
        assert a_wallet.balance() == 150

        assert transaction.valid_token(txn0a, a_wallet.wallet[0])
        assert transaction.valid_token(txn0b, a_wallet.wallet[1])
```

And start to iterate through a chain of transactions, verifying wallet state as various send and receive actions occur. 

```python
        # cannot send more than wallet total
        assert a_wallet.send(200, b_wallet.public_key) is None

        # A sends first token to B, with 50 in change (txn pending)
        _, txn1 = a_wallet.send(50, b_wallet.public_key)
        assert a_wallet.balance() == 50

        # rejecting the send restores A wallet
        assert len(a_wallet.pending) == 1
        a_wallet.reject_send(transaction.hash_txn(txn1))
        assert a_wallet.balance() == 150
        assert len(a_wallet.wallet) == 2
        assert len(a_wallet.pending) == 0

        # send again and confirm for A and B
        _, txn1 = a_wallet.send(50, b_wallet.public_key)

        a_wallet.confirm_send(transaction.hash_txn(txn1))
        assert a_wallet.balance() == 50
        assert a_wallet.pending == []
        a_wallet.receive(txn1)
        assert a_wallet.balance() == 100

        b_wallet.receive(txn1)
        assert b_wallet.balance() == 50
```

The testing works through a few more scenarios, abbreviated here but available [in the source](https://github.com/tkuriyama/toycoin/blob/master/blockchain/tests/test_wallet.py).

Incidentally, `pytest-cov` shows good coverage so far, though high coverage shouldn't be taken as infallibility.

```shell
---------- coverage: platform darwin, python 3.9.1-final-0 -----------
Name                     Stmts   Miss  Cover
--------------------------------------------
toycoin/hash.py              6      0   100%
toycoin/merkle.py          101     10    90%
toycoin/signature.py        26      0   100%
toycoin/transaction.py      45      1    98%
toycoin/utils.py             6      0   100%
toycoin/wallet.py           39      2    95%
--------------------------------------------
```

## Wrapping Up

The wallet module was written in tandem with the revised transaction model, since it was a lot easier to imagine how transactions would work with a consumer of the interface.

It's been a bit tricky to come up with these implementations, even though they are conceptually  simple. Maybe it's due to a few more considerations than usual:

- the functions are pure so far, but they need to play nicely with stateful actions and data eventually (i.e. interacting with the blockchain network and looking up previous blocks or transactions for verification, etc)

- the implementation and testing primarily focuses on correctness given honest actors, but it should also deal with bad actors in the way the the protocol specifies (i.e. trying not to introduce unintended vulnerabilities)

There's probably a lot of detail and nuance that's missing, but taking the first steps is the point of this exercise.

In such exercises -- and in life at large -- I'm often reminded of John Salvatier's essay, ["reality has a surprising amount of detail"](http://johnsalvatier.org/blog/2017/reality-has-a-surprising-amount-of-detail).


[Code on Github](https://github.com/tkuriyama/toycoin/tree/master/blockchain/toycoin)


## References

- [Nakamoto Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf)

