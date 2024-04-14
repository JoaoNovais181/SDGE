#!/usr/bin/env python

from node import *
import node
import json
import hashlib

serverHashes: list[str] = []
servers: list[str] = []
data = {}

# returns the name of the server in which to put the item with key given as argument
def searchNode(key) -> str:
    global serverHashes

    left: int = 0
    right: int = len(serverHashes) - 1
    keyHash: str = hashlib.sha1(str(key).encode("ascii")).hexdigest()


    while right-left > 1:

        mid = left + (right - left) // 2
        midHash = serverHashes[mid]

        if keyHash < midHash:
            right = mid - 1
        elif keyHash > midHash:
            left = mid + 1

    log(f"\n\nKey {key} is being sent to server {servers[right]} {serverHashes[right]}\n{serverHashes = }\n{servers = }\n{keyHash = }")

    return servers[right]

def sendChange(key, value):

    for n in node_ids():
        if n != node_id():
            send(n, type="fwd_msg", key=key, value=value)

@handler
def init(msg):
    global serverHashes, servers
    node.init(msg)
    aux = []
    for nodeID, n in [(server, server + f"/{num}") for server in node_ids() for num in range(0,2)]:
        aux.append((nodeID, hashlib.sha1(n.encode("ascii")).hexdigest()))
        aux.sort(key=lambda x: x[1])

        servers, serverHashes = map(list, list(zip(*aux)))

@handler
def read(msg, forwarded: bool = False):
    global data

    key = msg.body.key
    n = (forwarded and node_id()) or searchNode(key)

    if n == node_id():
        if key in data.keys():
            reply(msg, type="read_ok", value=data[key])
        else:
            reply(msg, type="error", code=20)
    else:
        send(n, type="fwd_msg", msg=msg)

@handler
def write(msg, forwarded: bool = False):
    global data

    key = msg.body.key
    value = msg.body.value

    n = (forwarded and node_id()) or searchNode(key)

    if n == node_id():
        data[key] = value
        reply(msg, type="write_ok")
    else:
        send(n, type="fwd_msg", msg=msg)

@handler
def cas(msg, forwarded: bool = False):
    global data

    key = msg.body.key

    n = (forwarded and node_id()) or searchNode(key)

    if n == node_id():

        fromVal = getattr(msg.body, "from")
        to = msg.body.to

        if key not in data.keys():
            reply(msg, type="error", code=20)
        elif data[key] != fromVal:
            reply(msg, type="error", code=22)
        else:
            data[key] = to
            reply(msg, type="cas_ok")
    else:
        send(n, type="fwd_msg", msg=msg)

@handler
def fwd_msg(msg):
    global data

    if msg.body.msg.body.type == "read":
        read(msg.body.msg, True)
    elif msg.body.msg.body.type == "write":
        write(msg.body.msg, True)
    else:
        cas(msg.body.msg, True)


if __name__ == "__main__":
    receive()
