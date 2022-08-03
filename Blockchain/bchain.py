from datetime import datetime
from email.mime import image
from xml.dom.minicompat import NodeList
from flask import render_template, jsonify, redirect, url_for, flash, request
import hashlib
import json
import sqlite3
from importlib_metadata import files

from numpy import block
from Blockchain.bfunctions import *
from time import *
from uuid import uuid4
from urllib.parse import urlparse
from Blockchain.form import *
import requests
from Blockchain.model import *
from Blockchain.utils import resent_email, save_picture
from Blockchain import app, db, bcrypt
from Blockchain.model import Transactions, Bminers, Users
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_login import login_user, current_user, logout_user, login_required



# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')
# initiate the Blockchain
blockchain = BlockChain()
#create genesis
#blockchain.create_genesis()
#Connect to database
sqliteConnection = sqlite3.connect('Blockchain\database.db')


@app.route('/', methods=['GET'])
def home():
    transactions = Transactions.query.all()
    length = len(Transactions.query.all())
    
    
    prev_hash = transactions
    receiver = Users.query.filter_by(username=Users.user_id).first()
    print(receiver)
    username = current_user.username
    balance = current_user.balance
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("index.html", title="Home", username=username,transactions=prev_hash, balance=balance, image_file=image_file, datetime=datetime.now())


@app.route('/mine', methods=['GET'])
def mine():
    global result
    node_list = list(blockchain.nodes)
    # get the miner ip
    miner_ip_address = request.remote_addr
    print(miner_ip_address)
    if len(node_list) == 0:
        return jsonify("Mining Revoked!")
    for node in node_list:
        if str(miner_ip_address) == node:
            # first we need to run the proof of work algorithm to calculate the new proof..
            last_block = blockchain.last_block
            last_proof = last_block['proof']
            proof = blockchain.proof_of_work(last_proof)

            # we must recieve reward for finding the proof in form of receiving 1 Coin
            blockchain.new_transaction(
                sender=node_identifier,
                recipient=node_identifier,
                amount=1,
            )
            # forge the new block by adding it to the chain
            previous_hash = blockchain.hash(last_block)
            block = blockchain.new_block(proof, previous_hash)

            response = {
                'message': "Forged new block.",
                'index': block['index'],
                'transactions': block['transactions'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
            }
            return jsonify(response, 200)
        else:
            return jsonify("Node not Authorised: " + miner_ip_address)
    print(node_list)
    return render_template('mine_response.html', response=response)



@app.route('/transaction/new', methods=['GET', 'POST'])
def new_transaction():
    values = request.get_json()
    print(values)
    required = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        return 'Missing values.', 400
    
    # create a new transaction
    index = blockchain.new_transaction(
        sender=values['sender'],
        recipient=values['recipient'],
        amount=values['amount']
    )

    response = {
        'message': f'Transaction will be added to the Block {index}',
    }

    return jsonify(response, 200)
    
@app.route('/new_transaction', methods=['GET', 'POST'])
@login_required
def new_transaction_page():
    form = NewTransactionForm()
    if form.validate_on_submit():
        recipient = str(form.recipient.data).lower()
        amount = form.amount.data
        my_id = Users.query.filter_by(email=current_user.email).first()
        receiver = Users.query.filter_by(email=recipient).first()
        data = {
                "sender": my_id.email,
                "recipient": recipient,
                "amount": amount
            }

        def generated_hash():
            # hashes a block
            # also make sure that the transactions are ordered otherwise we will have an inconsistent hashes!
            block_string = json.dumps(data, sort_keys=True).encode()
            return hashlib.sha256(block_string).hexdigest()
    
    
        
        current_balance = current_user.balance

        if receiver.email == current_user.email:
            flash(f"Sender cannot be self", "warning")
        
        else:
            if receiver is None:
                flash(f"Recipient {form.recipient.data} doesn't exist", "warning")
        
            else:
                if amount > current_balance:
                    flash(f"Wallet balance is {current_balance}. Not enough to send {amount}", "warning")

                else:
                    new_balance = current_balance - int(amount)
                    current_user.balance = new_balance
                    db.session.commit()

                    receiver.balance = receiver.balance + amount
                    db.session.commit()
                    
                    last_block = blockchain.last_block
                    last_proof = last_block['proof']
                    proof = blockchain.proof_of_work(last_proof)

                    
                    transaction = Transactions(
                        sender=current_user.email,
                        amount=amount,
                        recipient=receiver.email,
                        user_id=my_id.user_id,
                        hash=generated_hash(),
                    )
                    db.session.add(transaction)
                    db.session.commit()
                    flash(f"Sent {amount} to {receiver.email}", "success")
            
        requests.post('http://127.0.0.1:5000/transaction/new', json=data)
        return redirect(url_for('new_transaction_page'))
    username = current_user.username
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('transaction.html', title="New Transaction", username=username, image_file=image_file, form=form)

@app.route('/nodes/register', methods=['GET', 'POST'])
def register_nodes():
    values = request.get_json()

    # print('values', values)
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    # register each newly added node
    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': "New nodes have been added",
        'node_list': list(blockchain.nodes),
    }
    print(response)
    return jsonify(response), 201

@app.route('/register_nodes', methods=['GET', 'POST'])
def register_new_nodes():
    form = RegisterNodesForm()
    if form.validate_on_submit():
        miner_name = form.miner_name.data
        ip_address = form.ip_address.data
        email = form.email.data
        phone_number = form.phone_number.data
        
        data = {
            "nodes": [f"http://{ip_address}"],
        }

        miner = Bminers(
            miner_name=miner_name,
            email=email,
            ip_address=f"http://{ip_address}",
            phone_number=phone_number
        )
        
        db.session.add(miner)
        db.session.commit()
        flash("Node added to the Database.", 'success')
        requests.post('http://localhost:5000/nodes/register', json=data)
        return redirect(url_for('register_new_nodes'))
    node_list = Bminers.query.all()
    return render_template('nodeRegister.html', title="Register Nodes",form=form, nodes=node_list)


# Register new users
@app.route("/register-user", methods=['GET', 'POST'])
def register():
    """
    registers user
    :return:
    """
    # if current_user.is_authenticated:
    #     return redirect(url_for(''))
    form = UsersForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = Users(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()
        flash("Account added to the Database.", 'success')
        return redirect(url_for('login'))
    image_file = url_for('static', filename='profile_pics/default.png')
    return render_template("userRegister.html", form=form, title='User Signup', image_file=image_file)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def user_info():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('user_info'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    username = current_user.username
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',username=username, image_file=image_file, form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    login user
    :return:
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successfull', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        
    return render_template('login.html', title='User Login', form=form)


@app.route("/logout")
def logout():
    """
    logout user
    :return:
    """
    logout_user()
    return redirect(url_for('login'))


@app.route("/nodes")
def node_list():
    """
    logout user
    :return:
    """
    nodes = Bminers.query.all()
    if len(nodes) == 0:
        return render_template('reg_node.html', node=node_list)
    image_file = url_for('static', filename='profile_pics/default.png')
    return render_template('node_list.html',image_file=image_file, nodes=nodes)



def serializer(field):
    """
    serializer
    :param field:
    :return:
    """
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
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


@app.route("/verified_chain", methods=['GET'])
@login_required
def serialize():
    """
    renders home page
    :return:
    """

    data = jsonify([*map(serializer, Transactions.query.all())])
    return data


@app.route('/chain', methods=['GET'])
def full_chain():
    response = [*map(serializer, Transactions.query.all())]
    username = current_user.username
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('full_chain.html', title='Full Chain',username=username, image_file=image_file, blocks=response)

# @app.route('/chain2', methods=['GET'])
# def full_chain():
    

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if (replaced):
        response = [*map(serializer, Transactions.query.all())],
        message = 'Our chain has been replaced'
    else:
        message = 'Our chain is authoritative',
        response = [*map(serializer, Transactions.query.all())],
        length = len(Transactions.query.all())
    # jsonify(response)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('valid_chain.html', title='Valid Chain', response=response, message=message,image_file=image_file, length=length)


@app.route('/about', methods=['GET'])
@login_required
def about():
    username = current_user.username
    return render_template("about.html",username=username, title="About Page")

@app.route('/users', methods=['GET'])
def users():
    response =Users.query.all()
    username = current_user.username
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('users.html', title='Registered Users',username=username, image_file=image_file, blocks=response)