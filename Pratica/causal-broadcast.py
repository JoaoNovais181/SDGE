#!/usr/bin/env python

"""Obviously wrong implementation for 'cbcast' workload for Maelstrom"""

from node import *
import node
import json

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

@handler
def cbcast(msg):
    global delivered, vv
    vv[node_id()] += 1
    reply(msg, type='cbcast_ok', messages=delivered)
    delivered = []
    broadcast(type='fwd_msg', vv=vv, message=msg.body.message)

@handler
def fwd_msg(msg):
    global vv

    if testDeliverable(msg):
        delivered.append(msg.body.message)
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
