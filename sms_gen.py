from igraph import *
import json
import numpy as np
import random

def logSort(d):
    return d['time']

def createLog(numEpochs, msgsPerEpoch, graph, rr=True):
    # assume messages are only sent every second, choose msgsPerSec ppl to send, choose one of their 
    # neighbors to message every second, save in dictionary
    #TODO: force one conversation to definitely exist
    #TODO: in later seconds force sender to be people who sent a message responding
    log = []
    time = 0
    # force someone to message user 0
    markedSender = np.random.choice(graph.incident(0))
    senders = [(i,None) for i in np.random.choice(range(len(graph.vs)), msgsPerEpoch)]
    senders.append((markedSender, 0))
    print("markedSender: " + str(markedSender))
    for _ in range(numEpochs):
        for sender in senders:
            msg = {'time': time, 'type': 0, 'from': sender[0]} # time message was sent, and it is a message (type 0) not read receipt (type 1)
            if not sender[1] is None:
                msg['to'] = sender[1]
            else:
                try:
                    msg['to'] = np.random.choice(graph.incident(sender[0]))
                except ValueError:
                    # skip if person has no friends
                    continue

            log.append(msg)
            if rr:
                rrMsg = {'time': time+0.5, 'type': 1, 'from': msg['to'], 'to': msg['from']}
                log.append(rrMsg)
        time += 1
        # choose next epoch's senders, half from group, half will respond to messages
        senders = [(i, None) for i in np.random.choice(range(len(graph.vs)), msgsPerEpoch/2)]
        # want to do better at choosing who is responding, weighting towards new messages 
        senders += [(i['to'], i['from']) for i in np.random.choice(log, msgsPerEpoch - len(senders))]
        senders.append((markedSender, 0))
    
    log.sort(key=logSort)
    return log

        


def main():
    g = Graph.Read_Edgelist("graph.tmp")
    print('graph loaded')
    numUsers = len(g.vs)
    messagesPerUserPerDay = 50
    lengthOfCommunication = 10
    msgsPerSec = (numUsers*messagesPerUserPerDay)/(24*60*60)
    print("total messages per day: " + str(numUsers*messagesPerUserPerDay))
    print("total messages every second: " + str(numUsers*messagesPerUserPerDay/(24*60*60)))

    log = createLog(lengthOfCommunication, msgsPerSec, g)
    with open('log.json', 'w') as f:
        f.write(json.dumps(log))

if __name__ == "__main__":
    main()