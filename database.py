from email.mime import base
from tinydb import TinyDB, Query
from Cryptodome.Hash import SHA256
import bcrypt
import base58

db = TinyDB('database.json')

manufacturers = db.table('manufacturers')
users = db.table('users')
vehicles = db.table('vehicles')
blockchain = db.table('blockchain')


# ============================= VEHICLE OWNERSHIP ============================ #
def getOwner(vehicle_id):
    return users.get(
        Query().id == vehicles.search(Query().id == vehicle_id)[0].get('owner')
    )


def setOwner(vehicle_id, owner):
    vehicles.update(
        {'owner': owner},
        Query().id == vehicle_id
    )


# =================================== USER =================================== #
def createUser(user_id, user_type, password, personal_data: dict = {}):
    if getUser(user_id) is not None:
        return False

    address = base58.b58encode(SHA256.new(
        user_id.encode('utf-8')).hexdigest()).decode('utf-8')
    hash = bcrypt.hashpw(password.encode('utf-8'),
                         bcrypt.gensalt(10)).decode('utf-8')

    user_doc = {
        "id": user_id,
        "type": user_type,
        "pwhash": hash,
        "address": address,
        "ownedVehicles": [],
        "personalData": personal_data
    }

    users.insert(user_doc)
    return user_doc

def loginUser(user_id, password) -> dict | None:
    user = getUser(user_id)

    if not user or user is None:
        return None

    password = password.encode('utf-8')

    try:
        if bcrypt.checkpw(password, user.get('pwhash').encode('utf-8')):
            return user
        return None
    except ValueError:
        return None


def getUser(user_id):
    return users.get(Query().id == user_id)


def getUserVehicles(wallet_address):
    return vehicles.search(Query().owner == wallet_address)
