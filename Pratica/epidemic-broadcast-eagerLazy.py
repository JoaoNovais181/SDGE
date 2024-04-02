#!/usr/bin/env python

from node import *
import node
import json
import random

messages = []
delivered = {}
neighbours = []
F = 2 # FANOUT
LAZY_TTL = 1

@handler
def init(msg):
    global vv
    node.init(msg)

@handler
def topology(msg):
    global neighbours
    neighbours = list(random.sample(msg.body.topology.__dict__[node_id()], F))
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

if __name__ == "__main__":
    receive()
