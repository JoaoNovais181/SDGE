#!/usr/bin/env python

from node import *
import node
import json
import random

messages = []
delivered = {}
neighbours = []

# TODO decidir entre F e C

F = 2 # FANOUT
LAZY_TTL = 2
L = 4 # shuffle length
C = 5 # cache size
SHUFFLE_INTERVAL_TIME = 1000 # decidir como
SHUFFLE_INTERVAL_MSG = 10 # mensagens

def sendShuffle ():
    global neighbours

    subset = [elem for elem in random.sample(neighbours, L) if elem is not None]
    Q = random.choice(subset)
    subset[subset.index(Q)] = node_id()

    send(Q, type="shuffle", subset=subset)

@handler
def init(msg):
    global vv
    node.init(msg)
    neighbours = [None for _ in range(0,C)]

@handler
def topology(msg):
    global neighbours
    # neighbours = list(random.sample(msg.body.topology.__dict__[node_id()], F))
    for i,n in enumerate(list(msg.body.topology.__dict__[node_id()])):
        neighbours[i] = n
    log(f"{neighbours = }")
    reply(msg, type="topology_ok")

@handler
def broadcast(msg):
    global messages, neighbours
    messages.append(msg.body.message)
    delivered[msg.body.msg_id] = msg

    for node in neighbours:
        send(node, type="fwd_msg", message=msg.body.message, broadcast_id=msg.id, ttl=1)

    reply(msg, type="broadcast_ok")

@handler
def read(msg):
    reply(msg, type="read_ok", messages=messages)

## message distribution

@handler
def fwd_msg(msg):
    ttl = msg.body.ttl
    if msg.body.message not in messages:
        messages.append(msg.body.message)
        delivered[msg.body.broadcast_id] = msg

        if ttl < LAZY_TTL:
            for node in neighbours:
                send(node, type="fwd_msg", message=msg.body.message, broadcast_id=msg.body.broadcast_id, ttl=ttl+1)
        else:
            for node in neighbours:
                send(node, type="IHAVE", broadcast_id=msg.body.broadcast_id, ttl=ttl+1)

@handler
def IHAVE(msg):
    msg_id = msg.body.broadcast_id

    if msg_id not in delivered:
        reply(msg, type="IWANT", broadcast_id=msg_id, ttl=msg.body.ttl)

@handler
def IWANT(msg):

    reply(msg, type="fwd_msg", message=delivered[msg.body.broadcast_id].body.message, broadcast_id=msg.body.broadcast_id, ttl=msg.body.ttl)

## topology shuffling

@handler
def shuffle(msg):
    global neighbours

    subset = msg.body.subset
    P = msg.src
    
    old = [n for n in neighbours if n is not None]
    
    idx = 0
    noneCount = neighbours.count(None)
    for _ in range(noneCount):
        neighbours[neighbours.index(None)] = subset[idx]
        idx += 1

        if idx > len(subset):
            break

    idxOld = 0
    num = len(subset) - idx
    if num < 0:
        num = 0
    for _ in range(num):



if __name__ == "__main__":
    receive()
