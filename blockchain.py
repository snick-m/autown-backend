#!/usr/bin/python3.6
from datetime import datetime
from requests import request
from tinydb import Query
from miner import Miner

from multiprocessing import Process, Manager

from database import vehicles, setOwner

DIFFICULTY = 1      # Number of zeroes at the beginning of a new hash

def miners(block, blockchain):
    """Creates miners as independent processes and if a new block is
    validated it's added to the blockchain.

    :type block: dict
    :type blockchain: list
    """
    # create a shared variable and initialize it
    # the var is used for communication between processes (miners), when one
    # of them finds the hash of a block, the others will validate the block
    new_block = Manager().dict()
    new_block["block"] = None
    new_block["validated"] = None

    # in order to simplify this demo, miners will not communicate over p2p,
    # network but they will be simulated by independent processes
    # let's create 3 miners which will compete in finding a hash
    miners_lst = []
    for i in range(3):
        miners_lst.append(Miner(i, block, blockchain.all(), DIFFICULTY, new_block))

    # run each miner independently
    jobs = []
    for miner in miners_lst:
        p = Process(target=miner.mine)
        jobs.append(p)
        p.start()

    # join processes
    for p in jobs:
        # NOTE: the processes will be joined here, which means processes which
        # got earlier to this point will wait for the rest of them
        # ^^ above said, we'll wait until all processes validate the block,
        # if any of them rejects it, the block will not be put into the
        # blockchain in the next step
        p.join()

    # check if others have validated the block
    if new_block["validated"]:
        # add the block to the blockchain
        blockchain.insert(new_block["block"].get_block_obj(True))
        # TODO nice print so that it's more readable during presentation
        print_blockchain(blockchain.all())
        return new_block["block"].get_block_obj(True)
    else:
        print("The block has been rejected!")
        return None


def answer(msg, blockchain):
    print("\n")
    match msg["request"]:
        case "history":
            history = blockchain.search(Query().vehicle["id"] == msg["vehicleId"])
            return {"request": "history", "history": history}
        case "transfer":
            # find the block with the vehicleId
            vehicle = vehicles.get(Query().id == msg["vehicle"]["id"])
            if not vehicle:
                return {"request": "transfer", "message": "Invalid Vehicle ID"}
            
            response = miners(msg, blockchain)
            if response:
                setOwner(vehicle["id"], msg['vehicle']['owner'])
                return {"request": "transfer", "block": response, "message": "Vehicle transferred successfully"}
            else:
                return {"error": "Failed Transfer", "request": "transfer", "message": "Vehicle transfer failed"}
        case "manufacture":
            response = miners(msg, blockchain)
            if response:
                vehicles.insert(response['vehicle'])
                return {"request": "manufacture", "block": response, "message": "Vehicle manufactured successfully"}


def print_blockchain(blockchain):
    print("\n")
    print("BLOCKCHAIN CONTENT")
    for block in blockchain:
        print("\n")
        print(block)
    print("\n")

