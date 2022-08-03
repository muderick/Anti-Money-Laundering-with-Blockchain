import json
import hashlib
from urllib.parse import urlparse
from datetime import datetime
from flask_login import current_user
from matplotlib.font_manager import json_load
import requests

from Blockchain import app, db, bcrypt
from Blockchain.model import Transactions


BLOCKCHAIN_DIR = 'Blockchain\database.db'

class BlockChain(object):
    """ Main BlockChain class """

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        # create the genesis block
        self.new_block(previous_hash=1, proof=1000)
        
    
    
    def register_node(self, address):
        # add a new node to the list of nodes
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True
    
    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = len(Transactions.query.all())
                chain = [*map(serializer, Transactions.query.all())],

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        print(max_length)
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False
    
    def new_block(self, proof, previous_hash=None):
        # creates a new block in the blockchain
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender, recipient, amount):
        # adds a new transaction into the list of transactions
        # these transactions go into the next mined block
        self.current_transactions.append({
            "sender": current_user.username,
            "recipient": recipient,
            "data": amount,
        })
        #return int(self.last_block['index']) + 1

    @property
    def last_block(self):
        # returns last block in the chain
        return self.chain[-1]
    
    @staticmethod
    def hash(block):
        # hashes a block
        # also make sure that the transactions are ordered otherwise we will have insonsistent hashes!
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        # simple proof of work algorithm
        # find a number p' such as hash(pp') containing leading 4 zeros where p is the previous p'
        # p is the previous proof and p' is the new proof
        self.proof = 0
        while self.validate_proof(last_proof, self.proof) is False:
            self.proof += 1
        print(self.proof)
        return self.proof 

    @staticmethod
    def validate_proof(last_proof, proof):
        # validates the proof: does hash(last_proof, proof) contain 4 leading zeroes?
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
def serializer(self, field):
    """
    serializer
    :param field:
    :return:
    """
    last_block = last_block
    last_proof = last_block['proof']
    proof = self.proof_of_work(last_proof)
    for transaction in Transactions.query.all():

        if field.id == 1:
            prev_sender = 0
            prev_amount = 1
            prev_recipient = 0
            prev_hash = 1
            prev_proof = proof
        else:
            prev_sender = Transactions.query.get(field.id - 1).sender
            prev_amount = Transactions.query.get(field.id - 1).amount
            prev_recipient = Transactions.query.get(field.id - 1).recipient
            prev_hash = Transactions.query.get(field.id - 1).hash
            prev_proof = Transactions.query.get(field.id - 1).proof

        data = {
            "id": field.id,
            "sender": field.sender,
            "recipient": field.recipient,
            "amount": field.amount,
            "user_id": field.user_id,
            "hash": field.hash,
            "timestamp": field.timestamp,
            "proof": field.proof,
            "previous": {
                "previous_sender": prev_sender,
                "previous_recipient": prev_recipient,
                "previous_amount": prev_amount,
                "previous_hash": prev_hash,
                "previous_proof": prev_proof
            }
        }
    
    return data

