
import json
import hashlib
from urllib.parse import urlparse
from datetime import datetime
from flask_login import current_user
from matplotlib.font_manager import json_load
import requests

from Blockchain import app, db, bcrypt
import Blockchain
from Blockchain.model import Transactions, Block


BLOCKCHAIN_DIR = 'Blockchain\database.db'

class BlockChain(object):
    """ Main BlockChain class """
    
    difficulty = 2

    def __init__(self):
        self.chain = self.return_chain()
        self.uncornfirmed_transactions = []
        self.nodes = set()
        
    @staticmethod
    def return_chain():
        chain=[]
        block_list = Block.query.all()
        for block in block_list:
            transactions = []        
            txs = Transactions.query.filter_by(block_id=block.id).all()
            for tx in txs:
                t={'sender':tx.sender,'recipient':tx.recipient,'amount':tx.amount,'user_id':tx.user_id}
                ts = tx.timestamp
                if isinstance(ts,datetime):
                    t['timestamp']=ts.timestamp()
                transactions.append(t)
                b={"id":block.id,
                        "previous_hash":block.previous_hash, 
                        "proof":block.proof,
                        "block_hash":block.block_hash,
                        "transactions":transactions}
                bts = block.block_timestamp
                if isinstance(bts,datetime):
                    b["block_timestamp"]=bts.timestamp()
                chain.append(b)
            return chain
    
    # create the genesis block
    def create_genesis(self):
        dt = str(datetime.now())
        genesis = Block(0,"0",dt)
        db.session.add(genesis)
        db.session.commit()
        proof=self.proof_of_work(0)
        self.add_block(0,proof)
        
    def new_transaction(self, transaction):
        # adds a new transaction into the list of transactions
        # these transactions go into the next mined block
        self.unconfirmed_transactions.append(transaction)


    def mine(self):
        if not self.unconfirmed_transactions:
            return False
        
        last_block = self.last_block
        new_block = Block(index=last_block.index+1,transactions=self.unconfirmed_transactions,timestamp=str(datetime.now()),previous_hash=last_block.hash)
        proof=self.proof_work(new_block)
        self.add_block(new_block,proof)
        self.unconfirmed_transactions=[]
        return new_block.index
    
    
    @property
    def last_block(self):
        # returns last block in the chain
        return self.chain[-1]
    
    def proof_of_work(self, last_proof, block_id):
        # simple proof of work algorithm
        # find a number p' such as hash(pp') containing leading 4 zeros where p is the previous p'
        # p is the previous proof and p' is the new proof
        block = Block.query.get(block_id)
        block.proof = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0000'*self.difficulty):
            block.proof+=1
            computed_hash=block.compute_hash()
        db.session.add()
        db.session.commit()
        return computed_hash
    
    def add_block(self, block_id, proof):
        
        block = Block.query.get(block_id)
        
        if block_id==0:
            previous_hash="0"
        else:    
            previous_hash = self.last_block["block_hash"]

        if previous_hash != block.previous_hash:
            #print("hash did not match")
            #print(previous_hash)
            #print(block.previous_hash)
            Transactions.query.filter_by(block_id=block.id).delete()
            Block.query.filter_by(id=block.id).delete() 
            db.session.commit()
            return False

        if not self.is_valid_proof(block_id, proof):
            #print("is valid proof failed")
            Transactions.query.filter_by(block_id=block.id).delete()
            Block.query.filter_by(id=block.id).delete()
            db.session.commit()
            return False

        block.set_hash(proof)
        db.session.commit()
        self.chain=self.return_chain()
        return True
    
    
    @staticmethod
    def validate_proof(self, block_id, block_hash):
        # validates the proof: does hash(last_proof, proof) contain 4 leading zeroes?
        block = Block.query.get(block_id)
        return (block_hash.startswith('0000' * self.difficulty) and
                block_hash == block.compute_hash())
    
    
    @classmethod
    def is_valid(self,block,block_hash):
        #print(block)
        x= (block_hash.startswith('0000'*self.difficulty) and
                block_hash == self.hash(block))
        print("Inside is valid {}".format(x))
        return x
    
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        result = True
        previous_hash= "0"

        for block in chain:
            block_hash = block["block_hash"]
            del block["block_hash"] 
            if not self.is_valid(block,block_hash) or \
                    previous_hash != block["previous_hash"]:
                        result=False
                        break
            block["block_hash"],previous_hash = block_hash,block_hash
        #print("check chain vaildity result is {}".format(result))
        return result
        
    
    @staticmethod
    def create_instance(block):
        new_block=dict() 
        keys = list(block.keys())
        for key in keys:
            if key in ["id","transactions","block_timestamp","previous_hash","proof"]:
                new_block[key]=block[key]

        return new_block
    
    def register_node(self, address):
        # add a new node to the list of nodes
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    
    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """
        global blockchain
        neighbours = self.nodes
        longest_chain = None

        # We're only looking for chains longer than ours
        current_len = len(self.chain)
        

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            length = response.json()['length']
            chain = response.json()['chain']

            if length > current_len and self.check_chain_validity(chain):
                current_len=length
                longest_chain=chain
        print(longest_chain)
        # Replace our chain if we discovered a new, valid chain longer than ours
        if longest_chain:
            blockchain = longest_chain
            return True
        return False
    
    def announce_block(self, block):
        for node in self.nodes:
            url = "{}add_block".format(node)
            headers = {"Content-Type":"application/json"}
            requests.post(url, data=json.dumps(block.__dict__,sort_keys=True),headers=headers)
        
    @staticmethod
    def hash(block):
        # hashes a block
        # also make sure that the transactions are ordered otherwise we will have insonsistent hashes!
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    
    def create_chain_from_dump(self, chain_dump):
        self.create_genesis()
        for idx, block_data in enumerate(chain_dump):
            if idx==0:
                continue
            block = Block(block_data["index"],
                        block_data["transactions"],
                        block_data["timestamp"],
                        block_data["previous_hash"],
                        block_data["proof"])
            proof = block_data['hash']
            added = self.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
            
        return self