from Blockchain import app, db
from Blockchain.model import *

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)
