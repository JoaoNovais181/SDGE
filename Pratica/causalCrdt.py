#!/usr/bin/env python

"""Obviously wrong implementation for 'cbcast' workload for Maelstrom"""

from node import *
import node
import json

# CRDT state
c: int = 0 # auxiliary state
m: dict = {} # values

# operation counter
opCounter: int = 0

delivered = []
waiting = []

def broadcast(body={}, /, **kwds):
    for i in node_ids():
        if i != node_id():
            send(i, body, **kwds)

def apply(type, element, msg):
    opCounter += 1

    if type == "add":
        c[msg.src] += 1
        m[e] = (msg.src, c)
        
        reply(msg, type="add_ok")
    elif type == "remove":
        # c[msg.src] += 1 # irrelevante por enquanto
        if element in m.keys():
            m.pop(element)

        reply(msg, type="remove_ok")

    if opCounter % 100 == 0:

        for node in node_ids():
            if node != node_id():
                send(node, type="fwd_msg", m=m, c=c)

@handler
def init(msg):
    global vv
    node.init(msg)
    for i in node_ids():
        c[i] = 0

@handler
def add(msg):
    apply("add", msg.body.element)

@handler
def read(msg):
    reply(msg, type="read_ok", value=[key for key in m.keys()])

@handler
def remove(msg):
    prepared = prepare("remove", msg.body.element)

@handler
def fwd_msg(msg):
    global vv

    mMsg, cMsg = msg.body.m, msg.body.c

    ## Fazer o join do DotMap, em que para descobrir v(k) utilizo o Join do DotSet

if __name__ == "__main__":
    receive()
