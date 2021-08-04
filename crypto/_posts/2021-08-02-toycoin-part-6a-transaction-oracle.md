---
layout: post
title:  "Toycoin Part 6a: Networking Start: a Transaction Oracle"
date:   2021-08-02 09:00:00 -0500
tags:   python blockchain networking
---


**Note: the toycoin series of posts is for learning / illustrative purposes only; no part of it should be considered secure or useful for real-world purposes.**

Having done only a few [basic exercises](https://github.com/tkuriyama/toyserver) in networking, I tried to find some good resources for implementing a P2P network in Python. It turns out that... surprisingly, there aren't obviously good sources?

There's a list of options collected in [this article](https://blog.rfox.eu/en/Explorations/Python_p2p_libraries_and_frameworks.html), but none of them are very obvious (at least to me). The most informative one I found was [an older page](https://cs.berry.edu/~nhamid/p2p/framework-python.html), which uses Python 2 and threads.

The search for a more modern source -- ideally with a good introduction to `asyncio` -- led to Caleb Hattingh's [*Using Asyncio in Python*](https://www.oreilly.com/library/view/using-asyncio-in/9781492075325/)) from O'Reilly. Though on the short side, it lays out thoughtfully some of the sumbling blocks with `asyncio` (to start with, the complexity of its documentation for async beginners) and walks through the fundamentals from an application developer's perspective. Though P2P is not specifically discussed, there are enough worked examples of managing state in `asyncio` networking to get started.

## P2P Considerations

Two questions that arise early in considering a P2P network are:

1. how do you discover peers in the network?
2. how do you send / route messages to peers nodes in the network?

A P2P network needs to be bootstrapped somehow (e.g. with a set of canonical servers from which to lookup active nodes), so some degree of centralization is still required. For `toycoin`, there will just be a single, hard-coded node that is expected to be running, and serves as the bootstrap node.

For large networks, a full mesh (all nodes connected to all other nodes) is inefficient, so there is some routing and forwarding logic implemented by the P2P protocol. For the initial version of `toycoin`, network design is de-emphasized, so there will be a central relay server that broadcasts messages to and on behalf of all nodes.


## A Transaction Oracle

Hattingh's book has a very simple message protocool for sending bytes over TCP: a fixed number of bytes, indicating the size of the payload, followed by the payload itself.

```python

async def read_msg(stream: StreamReader) -> bytes:
    size_bytes = await stream.readexactly(4)
    size = int.from_bytes(size_bytes, byteorder='big')
    data = await stream.readexactly(size)
    return data


async def send_msg(stream: StreamWriter, data: bytes):
    size_bytes = len(data).to_bytes(4, byteorder='big')
    stream.writelines([size_bytes, data])
    await stream.drain()
```

Using this protocol, and an additional protocol of sending channel names before messages to broadcast to the channel, a [msg relay server](https://github.com/tkuriyama/toycoin/blob/master/blockchain/toycoin/network/relay.py) and [listener](https://github.com/tkuriyama/toycoin/blob/master/blockchain/toycoin/network/listener.py) are adapted with little modification from Hattingh's book.

Now, we want something that broadcasts transactions to the `toycoin` network of nodes. The purpose of such a transaction oracle is:

- provide transaction data for nodes to work on
- provide an authoritative source of truth, against which the results of the `toycoin` network blockchain can be compared against (i.e. the authoritative wallets should match the longest chain wallets, if all transactions in the blockchain are applied to the genesis wallets)

The main loop of the transaction oracle looks like this:

```python
async def main(args):
    """Transaction oracale main loop."""
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}: Transaction Oracle')
    reader, writer = await asyncio.open_connection(
        host=args.host, port=args.port)
    print(f'I am {writer.get_extra_info("sockname")}')

    channel = b'/connect'
    await send_msg(writer, channel)

    chan = args.channel.encode()
    try:
        txn_pairs, state = init_state()
        while True:
            await asyncio.sleep(random.randint(args.min_interval,
                                               args.max_interval))
            try:
                for txn_pair in txn_pairs:
                    data = serialize.pack_txn_pair(txn_pair).encode()
                    print(f'Sending {data[:19]}')
                    await send_msg(writer, chan)
                    await send_msg(writer, data)
                txn_pairs, state = update_state(state)

            except OSError:
                print('Connection ended.')
                break

    except asyncio.CancelledError:
        writer.close()
        await writer.wait_closed()
```

After networking initialization, the `init_state()` function initializes wallets with genesis transactions (magically, not in a particularly nice way). (Presumably, there is some special way to do this, and for minting new coins, for real protocols.)

Thereafter, there is a forever loop that waits some random interval and then broadcasts random transactions to the network.

The "random" transactions are of randomized value, but are valid by construction, and are applied immediately to the state (wallets) maintained by the transaction oracle, since the oracle maintains an independent source of truth in our toy network.


```python

OracleState = List[wallet.Wallet]

def update_state(state: OracleState
                 ) -> Tuple[List[transaction.TxnPair], OracleState]:
        """Generate a random transaction and update state of wallets."""
    print('\nGenerating new transaction...')
    print_state(state)

    while True:
        sender, receiver = draw_two(len(state) - 1)
        amount = min(random.randint(5, 15), state[sender].balance())
        if amount > 0:
            txn_pair = state[sender].send(amount,
                                          state[receiver].public_key)
            if not txn_pair:
                print('Unexpected send error...')
            else:
                print(f'Sending from wallet {sender} to {receiver}: {amount}')
                _, txn = txn_pair
                state[sender].confirm_send(transaction.hash_txn(txn))
                state[sender].receive(txn)
                state[receiver].receive(txn)
                break

    print_state(state)
    return ([txn_pair], state)
```

## Testing

Unit tests are written for helper functions like de/serialization and helpers. As for network activity, its randomized nature makes it a bit tricker to test programmatically. To get started, we can observe prints of network activity...

The relay server starts up, accepts two clients (a lister and the transaction oracle), and broadcasts transactions... 

```sh
% python relay.py                                                                                (master)toycoin
Remote ('127.0.0.1', 53346) subscribed to b'/topic/txn'
Remote ('127.0.0.1', 53347) subscribed to b'/connect'
Sending to b'/topic/txn': b'[[], "{\\"previous_h'...
Sending to b'/topic/txn': b'[[], "{\\"previous_h'...
Sending to b'/topic/txn': b'[["{\\"txn_hash\\": \\'...
Sending to b'/topic/txn': b'[["{\\"txn_hash\\": \\'...
Sending to b'/topic/txn': b'[["{\\"txn_hash\\": \\'...
Sending to b'/topic/txn': b'[["{\\"txn_hash\\": \\'...
^CRemote ('127.0.0.1', 53346) connection cancelled.
Remote ('127.0.0.1', 53346) closed
Remote ('127.0.0.1', 53347) connection cancelled.
Remote ('127.0.0.1', 53347) closed
```

The transaction oracle starts up, and after the genesis transactions, broadcasts four randomized transactions, each of which appear to modify the state of wallets in valid ways.

```sh
% python txn_oracle.py                                                                           (master)toycoin
Starting up 2dccacc0: Transaction Oracle
I am ('127.0.0.1', 53347)
Sending b'[[], "{\\"previous_h'
Sending b'[[], "{\\"previous_h'

Generating new transaction...
Wallet balances: 100, 50, 0, 0
Sending from wallet 1 to 2: 11
Wallet balances: 100, 39, 11, 0
Sending b'[["{\\"txn_hash\\": \\'

Generating new transaction...
Wallet balances: 100, 39, 11, 0
Sending from wallet 1 to 2: 7
Wallet balances: 100, 32, 18, 0
Sending b'[["{\\"txn_hash\\": \\'

Generating new transaction...
Wallet balances: 100, 32, 18, 0
Sending from wallet 0 to 2: 5
Wallet balances: 95, 32, 23, 0
Sending b'[["{\\"txn_hash\\": \\'

Generating new transaction...
Wallet balances: 95, 32, 23, 0
Sending from wallet 1 to 0: 15
Wallet balances: 110, 17, 23, 0
Sending b'[["{\\"txn_hash\\": \\'

Connection ended.
```

On the listening node, we see the transactions (and tokens that were used to fund the transactions), each of which correspond to those from the transaction oracle.


```sh
% python listener.py                                                                             (master)toycoin
Starting up bd1b5f2d
I am ('127.0.0.1', 53346)
Received by bd1b5f2d: 
--------------------------------------------------------------------------------
Tokens

Transaction
{"previous_hashes": [], "receiver": "LS0tLS1CRUdJTiBQVUJ...", "receiver_value": 100, "receiver_signature": "...", "sender": "Z2VuZXNpcw==...", "sender_change": 0, "sender_signature": "..."}
Connection ended.
Received by bd1b5f2d: 
--------------------------------------------------------------------------------
Tokens

Transaction
{"previous_hashes": [], "receiver": "LS0tLS1CRUdJTiBQVUJ...", "receiver_value": 50, "receiver_signature": "...", "sender": "Z2VuZXNpcw==...", "sender_change": 0, "sender_signature": "..."}
Connection ended.
Received by bd1b5f2d: 
--------------------------------------------------------------------------------
Tokens
{"txn_hash": "2U42SsK+F+uukb7zo3H...", "owner": "LS0tLS1CRUdJTiBQVUJ...", "value": 50, "signature": "..."}
Transaction
{"previous_hashes": ["2U42SsK+F+uukb7zo3H..."], "receiver": "LS0tLS1CRUdJTiBQVUJ...", "receiver_value": 11, "receiver_signature": "ecj2s7ayAqpx6Q2vQnu...", "sender": "LS0tLS1CRUdJTiBQVUJ...", "sender_change": 39, "sender_signature": "VLlyrLsvqd8FPZCgDMg..."}
Connection ended.
Received by bd1b5f2d: 
--------------------------------------------------------------------------------
Tokens
{"txn_hash": "pW5HL5c9paTNBinooQk...", "owner": "LS0tLS1CRUdJTiBQVUJ...", "value": 39, "signature": "VLlyrLsvqd8FPZCgDMg..."}
Transaction
{"previous_hashes": ["pW5HL5c9paTNBinooQk..."], "receiver": "LS0tLS1CRUdJTiBQVUJ...", "receiver_value": 7, "receiver_signature": "kdOYKQ5Ulsj6gU+hZ+1...", "sender": "LS0tLS1CRUdJTiBQVUJ...", "sender_change": 32, "sender_signature": "VroAxASsooX7kbs1r/C..."}
Connection ended.
Received by bd1b5f2d: 
--------------------------------------------------------------------------------
Tokens
{"txn_hash": "PqDcCIpU7S+Ubri+dPw...", "owner": "LS0tLS1CRUdJTiBQVUJ...", "value": 100, "signature": "..."}
Transaction
{"previous_hashes": ["PqDcCIpU7S+Ubri+dPw..."], "receiver": "LS0tLS1CRUdJTiBQVUJ...", "receiver_value": 5, "receiver_signature": "VlZFRRLbcXxIxizamOO...", "sender": "LS0tLS1CRUdJTiBQVUJ...", "sender_change": 95, "sender_signature": "uhTF6yHeVEL5FwRlnGW..."}
Connection ended.
Received by bd1b5f2d: 
--------------------------------------------------------------------------------
Tokens
{"txn_hash": "pbUvzecFNazv+83xlDX...", "owner": "LS0tLS1CRUdJTiBQVUJ...", "value": 32, "signature": "VroAxASsooX7kbs1r/C..."}
Transaction
{"previous_hashes": ["pbUvzecFNazv+83xlDX..."], "receiver": "LS0tLS1CRUdJTiBQVUJ...", "receiver_value": 15, "receiver_signature": "eP5XvuclHPQHa2iGEpH...", "sender": "LS0tLS1CRUdJTiBQVUJ...", "sender_change": 17, "sender_signature": "oL51f1zdyp4NC135MMC..."}
Connection ended.

Server closed.
```

So far, so good!


## Wrapping Up

The networking basics are in place, and we now have an authoritative transaction oracle, against which we can test the `toycoin` network.

 What remains is to write the logic fo network nodes, which will listen to network activity and compete to construct blocks using the proof-of-work algorithms previously written.

Once a basic network is implemented, there can be further expermentation with visualization of network activity, and the introduction of bad actor nodes, etc.

[Code on Github](https://github.com/tkuriyama/toycoin/tree/master/blockchain/toycoin/network) / [This Commit](https://github.com/tkuriyama/toycoin/commit/5629d1fcf9b6f12149020f12b41123a94fa4fa3a)


## References

- [Nakamoto Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf)
- [Caleb Hattingh: Using Aynscio in Python (O'Reilly)](https://www.oreilly.com/library/view/using-asyncio-in/9781492075325/)
- [Python P2P Libraries and Frameworks](https://blog.rfox.eu/en/Explorations/Python_p2p_libraries_and_frameworks.html)

