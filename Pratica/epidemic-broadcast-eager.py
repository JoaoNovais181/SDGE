#!/usr/bin/env python

from node import *
import node
import json
import random

messages = []
neighbours = []
F = 2

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

    for node in neighbours:
        send(node, type="fwd_msg", message=msg.body.message)

    reply(msg, type="broadcast_ok")

@handler
def read(msg):
    reply(msg, type="read_ok", messages=messages)

@handler
def fwd_msg(msg):
    if msg.body.message not in messages:
        messages.append(msg.body.message)

        for node in neighbours:
            send(node, type="fwd_msg", message=msg.body.message)

if __name__ == "__main__":
    receive()
