#!/usr/bin/env python

from node import *
import node
import json

store = {}
numServers: int = 0
separation: int = 0

group1: list[str] = []
group2: list[str] = []

proxy: str = ""

@handler
def init(msg):
    global numServers, separation, group1, group2, proxy

    node.init(msg)
    numServers = len(node_ids())
    serversPerGroup = numServers // 2
    evenServers = (numServers % 2) == 0
    separation = serversPerGroup

    group1 = node_ids()[0:serversPerGroup]
    group2 = node_ids()[serversPerGroup:]

    proxy = group1[0]

def append(key, value):
    if key not in store.keys():
        store[key] = []
    store[key].append(value)
    store[key].sort()

@handler
def txn(msg):
    global store

    op = msg.body.txn[0]
    key = op[1]

    if node_id() == proxy:

        
        desiredGroup = group1
        if key % numServers > separation:
            desiredGroup = group2

        desiredServer = desiredGroup[key % len(desiredGroup)]

        send(desiredServer, type="fwd_txn", clientMsg=msg)
        # if desiredServer == node_id():
        #     if op[0] == "r":
        #         reply(msg, type="txn_ok", txn=[["r", key, store.get(key)]])
        #     else:
        #         append(key, op[2])

        #         otherServer = otherGroup[key % len(otherGroup)]
        #         send(otherServer, type="propagate_txn", clientMsg=msg)
        #         # for n in node_ids():
        #         #     if n != node_id():
        #         #         send(n, type="fwd_write", key=key, value=op[2])

        #         reply(msg, type="txn_ok", txn=[["append", key, op[2]]])
        # else:
        #     send(desiredServer, type="fwd_txn", clientMsg=msg)

@handler
def fwd_txn_ok(msg):
    global store

    

@handler
def fwd_txn(msg):
    global store

    clientMsg = msg.body.clientMsg
    op = clientMsg.body.txn[0]
    log(op)
    key = op[1]

    otherGroup = group1
    if node_id() in group1:
        otherGroup = group2

    if op[0] == "r":
        reply(msg, type="fwd_txn_ok", txn=[["r", key, store.get(key)]], clientMsg=clientMsg)
    else:
        append(key, op[2])

        otherServer = otherGroup[key % len(otherGroup)]
        send(otherServer, type="propagate_txn", clientMsg=clientMsg)

        reply(msg, type="fwd_txn_ok", txn=[["append", key, op[2]]], clientMsg=clientMsg)

@handler
def propagate_txn(msg):
    global store

    clientMsg = msg.body.clientMsg
    op = clientMsg.body.txn[0]
    key = op[1]

    append(key, op[2])

    log(f"PROPAGATE: {msg.src} -> {clientMsg.body.txn = }")

    # reply(clientMsg, type="txn_ok", txn=[["append", key, op[2]]])

       

if __name__ == "__main__":
    receive()
