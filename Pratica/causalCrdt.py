#!/usr/bin/env python

from node import *
import node
import json

# CRDT state
c: dict = {} # auxiliary state
m: dict = {} # values

# operation counter
opCounter: int = 100

delivered = []
waiting = []

def broadcast(body={}, /, **kwds):
    for i in node_ids():
        if i != node_id():
            send(i, body, **kwds)

def apply(type, element, msg):
    global opCounter, c, m

    opCounter += 1

    if type == "add":
        c[node_id()] += 1
        m[element] = {(node_id(), c[node_id()])}
        
        reply(msg, type="add_ok")
    elif type == "remove":
        # c[msg.src] += 1 # irrelevante por enquanto
        if element in m.keys():
            m.pop(element)

        reply(msg, type="remove_ok")

    if opCounter % 10 == 0:

        broadcast(type="fwd_msg", m={k: list(v) for k,v in m.items()}, c=c)
                # send(node, type="fwd_msg", mc = {"m": m, "c":c})

def exceptDotSet(s, c):
    final = set()

    # c[i] = ci
    for i, ci in s:
        if i in c.keys() and c[i] <= ci:
            final.add((i, ci))

    return final

@handler
def init(msg):
    global c
    node.init(msg)
    for i in node_ids():
        c[i] = 0

@handler
def add(msg):
    apply("add", msg.body.element, msg)

@handler
def read(msg):
    reply(msg, type="read_ok", value=[key for key in m.keys()])

@handler
def remove(msg):
    apply("remove", msg.body.element, msg)

@handler
def fwd_msg(msg):
    global m, c
    
    def loadDict(d) -> dict:
        return json.loads(json.dumps(d, default= lambda s: vars(s)))

    mMsg = {int(k): v for k,v in loadDict(msg.body.m).items()}
    cMsg = loadDict(msg.body.c)

    mAux = {}
    cReunionCMsg = { k1: (c1 if c1 > c2 else c2) for (k1,c1), (_, c2) in zip(c.items(), cMsg.items()) }

    ## Fazer o join do DotMap, em que para descobrir v(k) utilizo o Join do DotSet

    
    ## Join DotMap
    for k in (list(m.keys()) + list(mMsg.keys())): 

        s = (k in m.keys() and m[k]) or set()
        s2 = (k in mMsg.keys() and set({tuple(v) for v in mMsg[k]})) or set()


        ## Join DotSet
        vK = (s & s2) | exceptDotSet(s, cMsg) | exceptDotSet(s2, c)
        # log(f"{s = } {s2 = } {(s & s2) = } |  {exceptDotSet(s, cMsg) = } | {exceptDotSet(s2, c) = }")
        
        if len(vK) > 0:
            mAux[k] = vK

    # log(f"JOIN\n\n{m = } {c = }\n{mMsg = } {cMsg = }\n{mAux = } {cReunionCMsg = }\n\n")
    m = mAux
    c = cReunionCMsg


if __name__ == "__main__":
    receive()
