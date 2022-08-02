from urllib import response
import socketio

from datetime import datetime

from aiohttp import web

from database import db, blockchain, getUser, getUserVehicles, loginUser
from blockchain import answer, print_blockchain

from tinydb import Query

# db.truncate()

HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
GENESIS_BLOCK = {
    "timestamp": datetime.now().isoformat(),
    "hash": "0",
    "vehicle": {
        "id": "GENESIS BLOCK"
    }
}

sio = socketio.AsyncServer(cors_allowed_origins='*')
# app = socketio.ASGIApp(sio)

app = web.Application()
sio.attach(app)


@sio.event
async def connect(sid, environ):
    print("Connected: ", sid)


@sio.event
def disconnect(sid):
    print("Disconnected: ", sid)


@sio.event
async def message(sid, data):
    print("\n")
    print("A new block received: ", data)

    response = {}

    try:
        if data['request']:
            response = answer(data, blockchain)
    except KeyError:
        # it was a block
        # response = miners(data, blockchain)
        response = {"error": "Invalid Request", "message": "Request Type missing"}

    await sio.send(response, to=sid)


@sio.event
async def login(sid, data):
    response = {
        "success": False,
        "message": "Invalid credentials"
    }

    try:
        user_doc = loginUser(data['username'], data['password'])
    except KeyError:
        return await sio.emit("loginAttempt", response, to=sid)

    if user_doc:
        user_doc['vehicles'] = getUserVehicles(user_doc['address'])
        async with sio.session(sid) as session:
            del user_doc['pwhash']
            session['user'] = user_doc

        response = {'success': True, 'user': user_doc}
        
        print('')
        print("User logged in: ", (await sio.get_session(sid))['user'])

    await sio.emit("loginAttempt", response, to=sid)

@sio.event
async def getUserData(sid):
    async with sio.session(sid) as session:
        print(session)
        user_id = session['user']['id']

    user_doc = getUser(user_id)
    user_doc['vehicles'] = getUserVehicles(user_doc['address'])
    del user_doc['pwhash']
    return user_doc

@sio.event
async def getVehicleHistory(sid, vehicleId):
    response = answer({"request": "history", "vehicleId": vehicleId}, blockchain)
    return response["history"]

@sio.event
async def logout(sid, data):
    response = {
        "success": False,
        "message": "Something went wrong"
    }

    async with sio.session(sid) as session:
        try:
            if session['user']:
                del session['user']
                response = {'success': True}
        except KeyError:
            response = {'success': True}

    await sio.emit("logoutAttempt", response, to=sid)


def main():
    # initialize blockchain by adding the genesis block
    # and create a file where all blocks will be appended
    # blockchain.truncate()

    if not blockchain.get(Query().hash == "0"):
        blockchain.insert(GENESIS_BLOCK)

    print_blockchain(blockchain.search(Query().timestamp.exists()))

    web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
