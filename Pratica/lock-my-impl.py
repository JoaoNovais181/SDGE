#!/usr/bin/env python

"""Single server (centralized) lock for Maelstrom

For 'lock' workload.  Will pass the test using, e.g.,
"--node-count 1 --concurrency 3n", but will fail using, .e.g.,
"--node-count 3".
"""

from node import *
from node import init as init2

requests = []
processes = {}
clock = 0

def insert(element):
    global requests

    requests.append(element)
    requests.sort(key=lambda val : val[1][1::])
    # requests.sort(key=lambda val : 1 if "c" in val[1] else 0)
    requests.sort(key=lambda val : val[0])
    requests.sort(key=lambda val : 0 if val[3] else 1)

    log(requests)

def changeHead():
    global requests
    if requests[0][1] == node_id():
        reply(requests[0][2], type="lock_ok")
        req = requests[0]
        requests[0] = (req[0],req[1],req[2], True)
        log(f"Changed {requests = }")

@handler
def init(msg):
    """Default handler for init message."""

    for node in msg.body.node_ids:
        if node != msg.body.node_id:
            processes[node] = 0

    init2(msg)

@handler
def forward_lock(msg):
    global clock, requests

    insert((msg.body.clock, msg.src, msg, False))
    clock = max(clock, msg.body.clock) + 1
    reply(msg, type="forward_lock_ack", clock=clock)
    clock += 1

@handler
def forward_lock_ack(msg):
    global processes, clock, requests
    processes[msg.src] = msg.body.clock
    
    lock = True
    for val in processes.values():
        if val <= requests[0][0]:
            lock = False
            break
    log(f"{processes} {requests} {lock}")

    if lock and not requests[0][3]:
        changeHead()

    clock += 1

@handler
def lock(msg):
    global clock
    for node in node_ids():
        if node != node_id():
            send(node, type='forward_lock', clock=clock)

    insert((clock, node_id(), msg, False))

    clock += 1

@handler
def unlock(msg):
    global requests, clock
    log(f"\n\n{requests}\n{msg}\n\n")
    if requests and requests[0][1] == node_id() and requests[0][2].src == msg.src and requests[0][3]:
        
        log(f"\t{requests[0]}")
        reply(msg, type="unlock_ok")
        oldAcquired = requests[0]

        if requests:
            requests.pop(0)

            if len(requests) > 0:
                changeHead()


        for node in node_ids():
            if node != node_id():
                send(node, type='forward_unlock', remove_clock=oldAcquired[0], clock=clock)

    else:
        reply(msg, type="error", code=22, text="lock not owned by " + msg.src)

    clock += 1

@handler
def forward_unlock(msg):
    global requests, clock

    log(f"\tacquired: {requests[0]}\n\trequests: {requests[0::]}\n\tmsg: {msg}")

    if requests:
        requests.pop(0)

        if len(requests) > 0:
            changeHead()

receive()
