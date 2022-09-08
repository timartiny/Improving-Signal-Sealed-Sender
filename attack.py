import json

def findRealSender(messages, personOfInterest):
    for msg in messages:
        if msg['to'] == personOfInterest:
            return msg['from']

def findTimeOfFirstMessageAfterTime(messages, personOfInterest, time):
    for msg in messages:
        if msg['to'] == personOfInterest and msg['time'] > time:
            return msg['time']

def readReceiptsAtTime(messages, time):
    rrs = []
    for msg in messages:
        if msg['time'] == time and msg['type'] == 1 :
            rrs.append(msg)
    
    return rrs

def attack(messages, personOfInterest, top5):
    # look at messages (ignoring "from") and determine which user was messaging personOfInterest
    # current assumptions: the rr is sent 0.5 seconds after messages always
    #                      messages always have a read receipt (rr)
    #                      user receives a message every second (no required replies)

    realSender = findRealSender(messages, personOfInterest)
    prb  = 0
    possibleSenders = []

    time = -1
    # print(realSender)
    while prb < 0.8:
        time = findTimeOfFirstMessageAfterTime(messages, personOfInterest, time)
        if not int(time) == time:
            break
        print(time)
        rrs = readReceiptsAtTime(messages, time+0.5)
        tmpSenders = [i['to'] for i in rrs]
        print(tmpSenders)
        if possibleSenders:
            possibleSenders = list(set(possibleSenders) & set(tmpSenders))
        else:
            possibleSenders = tmpSenders
        print(possibleSenders)
        prb = float(1)/ len(possibleSenders)
        print("Probability of guessing sender: " + str(prb))
    if len(possibleSenders) == 1 and realSender == possibleSenders[0]:
        print("Sender is: %s" % possibleSenders[0])
    elif realSender in possibleSenders:
        print("possible senders are: %s" % possibleSenders)

def main():
    with open('log.json','r') as f:
        log = json.loads(f.read())
    attack(log, 0)

if __name__== "__main__":
    main()