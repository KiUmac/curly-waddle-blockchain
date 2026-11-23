import hashlib
import json
import time


class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": self.transactions,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty):
        """Proof of work: find a nonce so the hash starts with `difficulty` zeros."""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()


class Blockchain:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.chain = []
        self.pending_transactions = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = Block(0, [], "0")
        genesis.mine(self.difficulty)
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        self.pending_transactions.append(
            {"sender": sender, "receiver": receiver, "amount": amount}
        )

    def mine_pending(self):
        if not self.pending_transactions:
            return None
        block = Block(len(self.chain), self.pending_transactions, self.last_block.hash)
        block.mine(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = []
        return block

    def is_valid(self):
        for i in range(1, len(self.chain)):
            cur, prev = self.chain[i], self.chain[i - 1]
            if cur.hash != cur.compute_hash():
                return False
            if cur.previous_hash != prev.hash:
                return False
            if not cur.hash.startswith("0" * self.difficulty):
                return False
        return True


if __name__ == "__main__":
    bc = Blockchain(difficulty=4)

    bc.add_transaction("Alice", "Bob", 50)
    bc.add_transaction("Bob", "Carol", 20)
    bc.mine_pending()

    bc.add_transaction("Carol", "Dave", 5)
    bc.mine_pending()

    for b in bc.chain:
        print(f"Block {b.index} | nonce={b.nonce} | hash={b.hash[:16]}... | prev={b.previous_hash[:16]}...")
        print("   transactions:", b.transactions)

    print("\nChain valid?", bc.is_valid())

    print("\nTampering with block 1...")
    bc.chain[1].transactions[0]["amount"] = 5000
    print("Chain valid?", bc.is_valid())
