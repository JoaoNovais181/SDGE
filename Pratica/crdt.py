#!/usr/bin/env python

"""Obviously wrong implementation for 'cbcast' workload for Maelstrom"""

from node import *
import node
import json

# CRDT state
c: int = 0 # auxiliary state
m: dict = {} # values

vv = {}
delivered = []
waiting = []

def testDeliverable(msg) -> bool:
    msgVV = json.loads(json.dumps(msg.body.vv, default=lambda s: vars(s)))
    src = msg.src

    srcTest = False
    # test src version number
    if vv[src] + 1 == msgVV[src]:
        srcTest = True

    # test version number for every other proccess
    otherTest = all(vv[k] >= msgVV[k] for k in node_ids() if k != src)

    log(f"{vv = } {msgVV = } {srcTest and otherTest = }")
    
    return (srcTest and otherTest)
    
def prepare(operation: str, e):
    global c
    if operation == "add":
        c = c + 1
        return (operation, e, (node_id(), c), (e in m.keys() and m[e]) or [])
    elif operation == "remove":
        return (operation, e, (e in m.keys() and m[e]) or [])

def effect(prepared: tuple):
    operation, *args = prepared
    log("OI\n\n\n\n\n\n")
    if operation == "add":
        e, d, r = args

        if e not in m.keys():
            m[e] = []

        for item in r:
            m[e].remove(item)

        m[e].append(d)

    elif operation == "remove":
        e, r = args

        if e in m.keys():

            for item in r:
                m[e].remove(item)

    log(f"{m = }\n\n")

    
def broadcast(body={}, /, **kwds):
    for i in node_ids():
        if i != node_id():
            send(i, body, **kwds)

@handler
def init(msg):
    global vv
    node.init(msg)
    for i in node_ids():
        vv[i] = 0

def cbcast(prepared: tuple):
    global delivered, vv
    vv[node_id()] += 1
    # reply(msg, type='cbcast_ok', messages=delivered)
    # delivered = []
    broadcast(type='fwd_msg', vv=vv, prepared=prepared)

@handler
def add(msg):
    prepared = prepare("add", msg.body.element)
    effect(prepared)
    cbcast(prepared)
    reply(msg, type="add_ok")

@handler
def read(msg):
    reply(msg, type="read_ok", value=[elem for elem, val in m.items() if len(val) > 0])

@handler
def remove(msg):
    prepared = prepare("remove", msg.body.element)
    effect(prepared)
    cbcast(prepared)
    reply(msg, type="remove_ok")

@handler
def fwd_msg(msg):
    global vv

    if testDeliverable(msg):
        log(msg.body.prepared)
        effect(msg.body.prepared)
        # delivered.append(msg.body.message)
        vv[msg.src] += 1
    else:
        waiting.append(msg)

    for m in waiting:
        if testDeliverable(m):
            waiting.remove(m)
            vv[m.src] += 1
            delivered.append(m.body.message)

if __name__ == "__main__":
    receive()
