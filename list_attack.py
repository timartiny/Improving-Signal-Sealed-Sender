#! /usr/bin/env python3
from collections import defaultdict, Counter
import json
import numpy as np
import random

def intersection(round, d, whole_round):
    round_senders = [a for a, _ in whole_round]
    for k, v in d.items():
        newKey = k + "&" + str(round)
        old_senders = []
        if "&" in k:
            old_senders = v
        else:
            old_senders = [b for b, _ in v]
        d[newKey] = list(set(old_senders) & set(round_senders))
    d[str(round)] = whole_round

def find_singletons(d):
    singletons = set()
    for _, v in d.items():
        if len(v) == 1:
            singletons.add(v[0])
    
    return singletons

def min_dict(d):
    small = -1
    for _, v in d.items():
        if small == -1:
            small = len(v)
        elif small > len(v):
            small = len(v)

    return small

def min_non_zero_dict(d):
    small = -1
    for _, v in d.items():
        if small == -1 and len(v) > 0:
            small = len(v)
        elif small > len(v) and len(v) > 0:
            small = len(v)

    return small

def random_round(d):
    round = random.choice(d.keys())
    while "&" in round:
        round = random.choice(d.keys())

    return d[round]

def generate_messages(num_msgs, num_users, msgs_mult, reply_mult, repeat_mult, record):
    # if no previous record generate msgs quickly
    msgs = []
    users = range(num_users)
    if not record or record[0] == []:
        for _i in range(num_msgs):
            sender = random.choice(users)
            receiver = random.choice(users)
            m = {"to": receiver, "from": sender, "len": 160}
            for _j in range(msgs_mult):
                msgs.append(m)
    # if the record exists, epochs have structure
    else:
        # first some of the messages are replies from previous epochs
        for _i in range(int(num_msgs*reply_mult)):
            m = random.choice(random.choice(record))
            m["to"], m["from"] = m["from"], m["to"]
            for _j in range(msgs_mult):
                msgs.append(m)
        
        # print("reply msgs: {:d}".format(len(msgs)))
        # now some part of the messages are simply repeated from previous epochs 
        for _i in range(int(num_msgs*repeat_mult)):
            m = random.choice(random.choice(record))
            for _j in range(msgs_mult):
                msgs.append(m)
        # print("reply and repeat msgs: {:d}".format(len(msgs)))
        
        
        # now the remainder of the msgs are randomly selected
        for _i in range(int(num_msgs - len(msgs)/msgs_mult)):
            sender = random.choice(users)
            receiver = random.choice(users)
            m = {"to": receiver, "from": sender, "len": 160}
            for _j in range(msgs_mult):
                msgs.append(m)
        # print("all msgs: {:d}".format(len(msgs)))
        
    return msgs
        
def run_x_messages(msgs_per_epoch, num_users, iterations, num_epochs, msgs_mult, reply_mult, repeat_mult, file_name, event_f, others_f):
    popular = 10
    # files = []
    # data_file = open(file_name, "a+")
    data_file = open(file_name, "w") # until it starts working
    # for i in range(1, num_epochs+1):
    #     files.append(open(file_name + "{:d}.dat".format(i), "a+"))
    data_dict = {"epoch": {}}
    for i in range(iterations):
        if i % 10 == 0:
            print("Iteration: {}".format(i + 1))
        
        # in this iteration, selected_sender will be Alice messaging Bob, selected receiver
        alice, bob, charlie = random.sample(range(num_users), 3)
        
        # keep track of how many msgs selected_sender needs to send to be identified, number of epochs necessary
        # epoch = 1
        # intersection = set(range(num_users))
        record = []
        count = Counter()
        most_common = count.most_common()
        # an epoch starts when a message (series of messages?) are being sent to Bob
        for epoch in range(1,num_epochs+1):
            if not epoch in data_dict["epoch"]:
                data_dict["epoch"][epoch] = []
            # f = files[epoch-1]

            # actual messages sent this epoch
            epoch_msgs = generate_messages(msgs_per_epoch, num_users, msgs_mult, reply_mult, repeat_mult, record)

            # now append delivery_receipts from previous epoch (unrealistic, does it matter?)
            last_round = []
            if record:
                last_round = record[-1]
            receipts = generate_messages(msgs_per_epoch, num_users, 1, 1, 0, [last_round])
            frequency = event_f + others_f

            bob_receipt = {"to": alice, "from": bob, "len": 160}
            decider = random.uniform(0,1)
            if decider < others_f:
                bob_receipt["to"] = charlie
            elif decider < frequency:
                bob_receipt["to"] = random.randint(0,num_users)
                bob_receipt["from"] = random.randint(0,num_users)
            receipts.append(bob_receipt)

            epoch_msgs += receipts
            record.append(epoch_msgs)

            tos = [d["to"] for d in epoch_msgs]
            count.update(set(tos))
            most_common = count.most_common()
            # intersection &= set(tos)
            
            
            if epoch >= 100:
                print("alice location: {}".format([x[0] for x in most_common].index(alice)))
            if epoch >= 1000:
                print("took over 1000 epochs")
                break

            # print("most_common: {}".format(most_common[:5]))
            success = 1
            if len(most_common) > 1: # then it is possible to fail
                success = 1 if most_common[0][0] == alice and most_common[0][1] > most_common[1][1] else 0

            ppl = [x[0] for x in most_common]
            alice_loc = ppl.index(alice) if alice in ppl else -1
            if alice_loc == -1:
                continue
            alice_class = [x[0] for x in most_common if x[1] == most_common[alice_loc][1]]
            # print("alice_class: {}".format(alice_class))
            alice_place = len(alice_class) + ppl.index(alice_class[0])
            data_dict["epoch"][epoch].append(alice_place)
            # data_file.write("\tepoch: {:3d}; alice place: {:3d}; success: {:d}\n".format(epoch, alice_place, success))
            # data_file.flush()
        
    s = json.dumps(data_dict)
    data_file.write(s + "\n")
    data_file.flush()
    data_file.close()

def variant_3(msgs_per_epoch, num_users, iterations, non_bob_epochs, num_pop_users, num_other_senders, num_epochs, msgs_mult, reply_mult, repeat_mult, file_name, event_f, others_f):
    # files = []
    # data_file = open(file_name, "a+")
    data_file = open(file_name, "w") # until it starts working
    # for i in range(1, num_epochs+1):
    #     files.append(open(file_name + "{:d}.dat".format(i), "a+"))
    data_dict = {"epoch": {}}
    for i in range(iterations):
        if i % 10 == 0:
            print("Iteration: {}".format(i + 1))
        
        # in this iteration, selected_sender will be Alice messaging Bob, selected receiver
        population = range(num_users)
        pop_users = random.sample(population, num_pop_users)
        population = [x for x in population if x not in pop_users]
        alice, bob = random.sample(population, 2)
        population.remove(alice)
        population.remove(bob)
        other_senders = random.sample(population, num_other_senders)
        
        # keep track of how many msgs selected_sender needs to send to be identified, number of epochs necessary
        # epoch = 1
        # intersection = set(range(num_users))
        record = []
        count = Counter()
        most_common = count.most_common()
        # an epoch starts when a message (series of messages?) are being sent to Bob
        for epoch in range(1,num_epochs+1):
            if not epoch in data_dict["epoch"]:
                data_dict["epoch"][epoch] = {"min": [], "max":[]}
            # f = files[epoch-1]

            # actual messages sent this epoch
            epoch_msgs = generate_messages(msgs_per_epoch, num_users, msgs_mult, reply_mult, repeat_mult, record)

            for pu in pop_users:
                epoch_msgs.append({"to": pu, "from": random.choice(population), "len": 160})


            # now append delivery_receipts from previous epoch (unrealistic, does it matter?)
            # last_round = []
            # if record:
            #     last_round = record[-1]
            # receipts = generate_messages(msgs_per_epoch, num_users, 1, 1, 0, [last_round])
            frequency = event_f + others_f

            bob_receipt = {"to": random.choice(other_senders + [alice]), "from": bob, "len": 160}
            decider = random.uniform(0,1)
            if decider < frequency:
                bob_receipt["to"] = random.randint(0,num_users)
                bob_receipt["from"] = random.randint(0,num_users)
            epoch_msgs.append(bob_receipt)

            # epoch_msgs += receipts
            record.append(epoch_msgs)

            tos = [d["to"] for d in epoch_msgs]
            count.update(set(tos))
            most_common = count.most_common()
            
            if epoch >= 100:
                print("alice location: {}".format([x[0] for x in most_common].index(alice)))
            if epoch >= 1000:
                print("took over 1000 epochs")
                break

            # print("most_common: {}".format(most_common[:5]))
            success = 1
            if len(most_common) > 1: # then it is possible to fail
                success = 1 if most_common[0][0] == alice and most_common[0][1] > most_common[1][1] else 0

            ppl = [x[0] for x in most_common]
            alice_loc = ppl.index(alice) if alice in ppl else -1
            if alice_loc == -1:
                continue
            alice_class = [x[0] for x in most_common if x[1] == most_common[alice_loc][1]]
            # print("alice_class: {}".format(alice_class))
            alice_place = len(alice_class) + ppl.index(alice_class[0])
            places = [alice_place]
            for sender in other_senders:
                sender_loc = ppl.index(sender) if sender in ppl else -1
                if sender_loc == -1:
                    # places.append(msgs_per_epoch)
                    continue
                sender_class = [x[0] for x in most_common if x[1] == most_common[sender_loc][1]]
                # print("alice_class: {}".format(alice_class))
                sender_place = len(sender_class) + ppl.index(sender_class[0])
                places.append(sender_place)
            

            # print("alice_place: {}".format(alice_place))
            # data_dict["epoch"][epoch]["alice"].append(alice_place)
            data_dict["epoch"][epoch]["min"].append(min(places))
            data_dict["epoch"][epoch]["max"].append(max(places))
            # data_file.write("\tepoch: {:3d}; alice place: {:3d}; success: {:d}\n".format(epoch, alice_place, success))
            # data_file.flush()

            # now add non_bob_epoch number of epochs, where we subtract those ppl from count
            for _ in range(non_bob_epochs):
                epoch_msgs = generate_messages(msgs_per_epoch, num_users, msgs_mult, reply_mult, repeat_mult, record)
                for pu in pop_users:
                    epoch_msgs.append({"to": pu, "from": random.choice(population), "len": 160})
                # receipts = generate_messages(msgs_per_epoch, num_users, 1, 1, 0, [last_round])
                tos = [d["to"] for d in epoch_msgs]
                tos = set(tos)
                # for s in other_senders + [alice]:
                #     if s in tos:
                #         tos.remove(s)
                count.subtract(set(tos))
                most_common = count.most_common()
                ppl = [x[0] for x in most_common]
                alice_loc = ppl.index(alice) if alice in ppl else -1
                if alice_loc == -1:
                    continue
                alice_class = [x[0] for x in most_common if x[1] == most_common[alice_loc][1]]
                # print("alice_class: {}".format(alice_class))
                alice_place = len(alice_class) + ppl.index(alice_class[0])
                # print("alice_place after dummy rounds: {}".format(alice_place))
        
    s = json.dumps(data_dict)
    data_file.write(s + "\n")
    data_file.flush()
    data_file.close()


def run_updated_attack(msgs_per_epoch, num_users, iterations, msgs_mult, reply_mult, repeat_mult, file_name, event_f, others_f):
    popular = 10
    with open(file_name, 'w') as f:
        for i in range(iterations):
            # in this iteration, selected_sender will be Alice messaging Bob, selected receiver
            alice, bob, charlie = random.sample(range(num_users), 3)
            
            # keep track of how many msgs selected_sender needs to send to be identified, number of epochs necessary
            epoch = 1
            # intersection = set(range(num_users))
            record = []
            count = Counter()
            most_common = count.most_common()
            # an epoch starts when a message (series of messages?) are being sent to Bob
            # print("alice: {:d}, bob: {:d}, charlie: {:d}".format(alice, bob, charlie))
            f.write("alice: {:d}, bob: {:d}, charlie: {:d}\n".format(alice, bob, charlie))
            f.flush()
            # while (not most_common) or (not alice in [x[0] for x in most_common][:popular]):
            # while (not most_common) or not (alice == most_common[0][0] and most_common[0][1] > most_common[1][1]):
            while epoch < 101:
                # actual messages sent this epoch
                epoch_msgs = generate_messages(msgs_per_epoch, num_users, msgs_mult, reply_mult, repeat_mult, record)

                # now append delivery_receipts from previous epoch 
                last_round = []
                if record:
                    last_round = record[-1]
                receipts = generate_messages(msgs_per_epoch, num_users, 1, 1, 0, [last_round])
                frequency = event_f + others_f

                bob_receipt = {"to": alice, "from": bob, "len": 160}
                decider = random.uniform(0,1)
                if decider < others_f:
                    bob_receipt["to"] = charlie
                elif decider < frequency:
                    bob_receipt["to"] = random.randint(0,num_users)
                    bob_receipt["from"] = random.randint(0,num_users)
                receipts.append(bob_receipt)

                epoch_msgs += receipts
                record.append(epoch_msgs)

                tos = [d["to"] for d in epoch_msgs]
                count.update(set(tos))
                most_common = count.most_common()
                ppl = [x[0] for x in most_common]
                # intersection &= set(tos)
                
                alice_loc = ppl.index(alice) if alice in ppl else -1
                if alice_loc == -1:
                    continue
                alice_class = [x[0] for x in most_common if x[1] == most_common[alice_loc][1]]
                # print("alice_class: {}".format(alice_class))
                alice_place = len(alice_class) + ppl.index(alice_class[0])
                f.write("\tepoch: {:d}; alice_place: {}\n".format(epoch, alice_place))
                f.flush()
                
                # if epoch >= 100:
                #     print("alice location: {}".format([x[0] for x in most_common].index(alice)))
                if epoch >= 1000:
                    print("took over 1000 epochs")
                    break
                epoch +=1
            print("alice index: {}, alice: {}, epochs: {}".format([x[0] for x in most_common].index(alice), alice, epoch-1))
            # f.write("\n")
            # f.flush()

def run_attack(msgs_per_epoch, num_users, iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, file_name, num_messengers):
    with open(file_name, 'w') as f:
        for i in range(iterations):
            possible_senders = range(num_users)
            selected_senders = [] 
            for _ in range(num_messengers): 
                selected_senders.append(random.choice(possible_senders))
            selected_receiver = random.choice(possible_senders)
            previous_senders = {}
            chosen = []
            msg = 1
            # print("selected_senders: {}".format(selected_senders))
            # while len(possible_senders) > 1:
            while len(find_singletons(previous_senders)) < num_messengers:
                # print("found senders: {}".format(len(find_singletons(previous_senders))))
                # print("msg: {}".format(msg))
                # print("len(possible_senders): {}".format(len(possible_senders)))
                f.write(str(min_non_zero_dict(previous_senders)) + ", ")
                f.flush()
                # print("min_dict: {}".format(str(min_non_zero_dict(previous_senders))))
                chosen_sender = random.choice(selected_senders)
                if not chosen:
                    for j in range(int(msgs_per_epoch*msgs_mult)):
                        chosen.append((random.choice(possible_senders), random.choice(possible_senders)))
                    # chosen = random.sample(possible_senders, msgs_per_epoch*msgs_mult)
                    # previous_senders[msg] = chosen 
                    chosen.append((chosen_sender, selected_receiver))
                    possible_senders = [a for a,_ in chosen]
                else:
                    chosen = []
                    # this is mimicing the more complicated C program that randomly selects 1/4 of messages to be from a previous epoch
                    # print("reply_mult: {}, int(msgs_per_epoch*reply_mult): {}".format(reply_mult, int(msgs_per_epoch*reply_mult)))
                    for j in range(int(msgs_per_epoch*reply_mult)):
                        tmp = random.choice(random_round(previous_senders)) 
                        chosen.append((tmp[1], tmp[0]))
                    # print("len(chosen): {}, msgs_per_epoch: {}".format(len(chosen), msgs_per_epoch))
                    # print("repeat_mult: {}, int(msgs_per_epoch*repeat_mult): {}".format(repeat_mult, int(msgs_per_epoch*repeat_mult)))
                    print("reply msgs: {:d}".format(len(chosen)))
                    for j in range(int(msgs_per_epoch*repeat_mult)):
                        chosen.append(random.choice(random_round(previous_senders))) # double choice here because previous senders is a dictionary with senders from each msg epoch
                    # print("len(chosen): {}, msgs_per_epoch: {}".format(len(chosen), msgs_per_epoch))
                    # print("fill_mult: {}, int(msgs_per_epoch*fill_mult): {}".format(fill_mult, int(msgs_per_epoch*fill_mult)))
                    print("repeat and reply msgs: {:d}".format(len(chosen)))
                    for j in range(int(msgs_per_epoch*fill_mult)):
                        chosen.append((random.choice(range(num_users)), random.choice(range(num_users))))
                    chosen.append((chosen_sender, selected_receiver))
                    print("all msgs: {:d}".format(len(chosen)))
                    # now intersect chosen and possible_senders
                    # possible_senders = list(set(possible_senders) & set([a for a,_ in chosen]))

                intersection(msg, previous_senders, chosen)
                    # print("len(chosen): {}, msgs_per_epoch: {}".format(len(chosen), msgs_per_epoch))
                # previous_senders[msg] = chosen # this means that future selections will be biased towards repeats selected from previous msgs
                if msg >= 1000:
                    break
                msg += 1
            f.write(str(min_non_zero_dict(previous_senders)) + "\n")
            f.flush()

def reply_repeat_fill_list_test():
    msgs_per_user_per_day = 50
    user_range = range(10000, 1005000, 5000)
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.25
    fill_mult = 0.5

    for num_users in user_range:
        print("num_users: " + str(num_users) + " mult: " + str(msgs_mult))
        msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
        if msgs_per_epoch <= 1:
            print("Not enough msgs in each epoch")
            exit(0)
        

        max_iterations = 100

        run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_" + str(num_users) + "_reply_repeat_fill.dat")

def reply_repeat_list_test():
    msgs_per_user_per_day = 50
    user_range = range(10000, 1005000, 5000)
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.25
    fill_mult = 0.0

    for num_users in user_range:
        print("num_users: " + str(num_users) + " mult: " + str(msgs_mult))
        msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
        if msgs_per_epoch <= 1:
            print("Not enough msgs in each epoch")
            exit(0)
        

        max_iterations = 100

        run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_" + str(num_users) + "_reply_repeat.dat")

def reply_fill_list_test():
    msgs_per_user_per_day = 50
    user_range = range(10000, 1005000, 5000)
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.00
    fill_mult = 0.5

    for num_users in user_range:
        print("num_users: " + str(num_users) + " mult: " + str(msgs_mult))
        msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
        if msgs_per_epoch <= 1:
            print("Not enough msgs in each epoch")
            exit(0)
        

        max_iterations = 100

        run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_" + str(num_users) + "_reply_fill.dat")

def repeat_fill_list_test():
    msgs_per_user_per_day = 50
    user_range = range(10000, 1005000, 5000)
    msgs_mult = 1
    reply_mult = 0.00
    repeat_mult = 0.25
    fill_mult = 0.5

    for num_users in user_range:
        print("num_users: " + str(num_users) + " mult: " + str(msgs_mult))
        msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
        if msgs_per_epoch <= 1:
            print("Not enough msgs in each epoch")
            exit(0)
        

        max_iterations = 100

        run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_" + str(num_users) + "_repeat_fill.dat")

def reply_list_test():
    msgs_per_user_per_day = 50
    user_range = range(10000, 1005000, 5000)
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.00
    fill_mult = 0.0

    for num_users in user_range:
        print("num_users: " + str(num_users) + " mult: " + str(msgs_mult))
        msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
        if msgs_per_epoch <= 1:
            print("Not enough msgs in each epoch")
            exit(0)
        

        max_iterations = 100

        run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_" + str(num_users) + "_reply.dat")

def repeat_list_test():
    msgs_per_user_per_day = 50
    user_range = range(10000, 1005000, 5000)
    msgs_mult = 1
    reply_mult = 0.00
    repeat_mult = 0.25
    fill_mult = 0.0

    for num_users in user_range:
        print("num_users: " + str(num_users) + " mult: " + str(msgs_mult))
        msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
        if msgs_per_epoch <= 1:
            print("Not enough msgs in each epoch")
            exit(0)
        

        max_iterations = 100

        run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_" + str(num_users) + "_repeat.dat")

def fill_list_test():
    msgs_per_user_per_day = 50
    user_range = range(10000, 1005000, 5000)
    msgs_mult = 1
    reply_mult = 0.00
    repeat_mult = 0.00
    fill_mult = 0.5

    for num_users in user_range:
        print("num_users: " + str(num_users) + " mult: " + str(msgs_mult))
        msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
        if msgs_per_epoch <= 1:
            print("Not enough msgs in each epoch")
            exit(0)
        

        max_iterations = 100

        run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_" + str(num_users) + "_fill.dat")

def repeat_percent_test(): 
    msgs_per_user_per_day = 50
    mults = np.arange(0.01, 1.01, 0.01)
    # mults = np.arange(0.99, 1.01, 0.01)
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.25
    fill_mult = 0.5


    for repeat_mult in mults:
        reply_mult = (1-repeat_mult)/3
        fill_mult = 1 - reply_mult - repeat_mult
        user_range = [50000,100000, 250000, 500000]
        # user_range = [10000]

        for num_users in user_range:
            print("num_users: " + str(num_users) + " mult: " + str(repeat_mult))
            msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
            if msgs_per_epoch <= 1:
                print("Not enough msgs in each epoch")
                exit(0)
            

            max_iterations = 100 
            # max_iterations = 5 

            run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_percentage_" + str(repeat_mult) + "_" + str(num_users) + ".dat", 1)

def multiple_senders_test(): 
    msgs_per_user_per_day = 50
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.25
    fill_mult = 0.5
    num_senders = np.arange(1, 11, 1)


    for num_messengers in num_senders:
        user_range = [50000,100000, 250000, 500000]

        for num_users in user_range:
            print("num_users: " + str(num_users) + " num_messengers: " + str(num_messengers))
            msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))*msgs_mult
            if msgs_per_epoch <= 1:
                print("Not enough msgs in each epoch")
                exit(0)
            

            max_iterations = 100

            run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_messengers_" + str(num_messengers) + "_" + str(num_users) + ".dat", num_messengers)

def message_rate_test(): 
    msgs_per_user_per_day = np.arange(4, 1001, 1)
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.25
    fill_mult = 0.5
    num_senders = 1


    for msg_rate in msgs_per_user_per_day:
        user_range = [50000,100000, 250000, 500000]

        for num_users in user_range:
            print("num_users: " + str(num_users) + " msg_rate: " + str(msg_rate))
            msgs_per_epoch = ((msg_rate*num_users)/(24*60*60))*msgs_mult
            if msgs_per_epoch <= 1:
                print("Not enough msgs in each epoch")
                exit(0)
            

            max_iterations = 100

            run_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, fill_mult, "data/list_python_msg_rate_" + str(msg_rate) + "_" + str(num_users) + ".dat", num_senders)

def updated_attack_test():
    msgs_per_user_per_day = 50
    msgs_mult = 3
    reply_mult = 0.25
    repeat_mult = 0.25
    user_range = [50*(10**3), 100*(10**3), 250*(10**3), 500*(10**3), 10**6]
    event_f = 0.33
    others_f = 0

    for num_users in user_range:
        print("num_users: " + str(num_users) + " mult: " + str(msgs_mult))
        msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))
        if msgs_per_epoch <= 1:
            print("Not enough msgs in each epoch")
            exit(0)
        

        max_iterations = 100 
        # max_iterations = 5 

        run_updated_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, "data/updated_attack_{:d}_{:d}.dat".format(msgs_mult, num_users), event_f, others_f)
        # run_updated_attack(msgs_per_epoch, num_users, max_iterations, 1, reply_mult, repeat_mult, "data/updated_attack_{:d}_{:d}.dat".format(1, num_users))
        # run_attack(msgs_per_epoch*3, num_users, max_iterations, 1, reply_mult, repeat_mult, 0.5, "data/old_attack_{:d}_{:d}".format(num_users, msgs_per_epoch*3), 1)

def run_x_messages_test():
    msgs_per_user_per_day = 50
    msgs_mult = 3
    reply_mult = 0.25
    repeat_mult = 0.25
    num_users = 10**6
    event_f = 0.33
    others_f = 0
    num_msgs_range = range(1, 30)
    num_msgs = 30
    msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))

    # for num_msgs in num_msgs_range:
    #     print("num_users: {}, mult: {}, num_msgs: {}".format(num_users, msgs_mult, num_msgs))
    #     if msgs_per_epoch <= 1:
    #         print("Not enough msgs in each epoch")
    #         exit(0)
        

    max_iterations = 100 
    # max_iterations = 5 

    run_x_messages(msgs_per_epoch, num_users, max_iterations, num_msgs, msgs_mult, reply_mult, repeat_mult, "data/num_msgs_attack_{:d}_{:d}_".format(msgs_mult, num_users), event_f, others_f)
    # run_updated_attack(msgs_per_epoch, num_users, max_iterations, 1, reply_mult, repeat_mult, "data/updated_attack_{:d}_{:d}.dat".format(1, num_users))
    # run_attack(msgs_per_epoch*3, num_users, max_iterations, 1, reply_mult, repeat_mult, 0.5, "data/old_attack_{:d}_{:d}".format(num_users, msgs_per_epoch*3), 1)

def response_percentage_test():
    msgs_per_user_per_day = 50
    msgs_mult = 3
    reply_mult = 0.25
    repeat_mult = 0.25
    num_users = 10**6
    # event_f = 0.33
    others_f = 0
    num_msgs = 100
    msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))
    event_fs = np.arange(0.1, 1.0, 0.1)


    # max_iterations = 1000
    max_iterations = 5 
    for event_f in event_fs:
        print("num users:{:9d}, event_f: {:0.02f}".format(num_users, event_f))
        run_x_messages(msgs_per_epoch, num_users, max_iterations, num_msgs, msgs_mult, reply_mult, repeat_mult, "data/response_percentage_test_{:d}_{:d}_{:0.02f}_".format(msgs_mult, num_users, event_f), event_f, others_f)

def rank_response_percentage_test():
    msgs_per_user_per_day = 50
    msgs_mult = 3
    reply_mult = 0.25
    repeat_mult = 0.25
    num_users = 10**6
    # event_f = 0.33
    others_f = 0
    # num_msgs = 100
    msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))
    event_fs = np.arange(0.1, 1.0, 0.2)


    # max_iterations = 1000
    max_iterations = 5 
    for event_f in event_fs:
        print("num users:{:9d}, event_f: {:0.02f}".format(num_users, event_f))
        run_updated_attack(msgs_per_epoch, num_users, max_iterations, msgs_mult, reply_mult, repeat_mult, "data/rank_response_attack_{:d}_{:d}_{:0.02f}.dat".format(msgs_mult, num_users, event_f), event_f, others_f)
        # run_x_messages(msgs_per_epoch, num_users, max_iterations, num_msgs, msgs_mult, reply_mult, repeat_mult, "data/response_percentage_test_{:d}_{:d}_{:0.02f}_".format(msgs_mult, num_users, event_f), event_f, others_f)

def msgs_per_epoch_test():
    # msgs_per_user_per_day = 50
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.25
    num_users = 10**6
    event_f = 0.00
    others_f = 0
    num_epochs = 100
    # msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))

    # for num_msgs in num_msgs_range:
    #     print("num_users: {}, mult: {}, num_msgs: {}".format(num_users, msgs_mult, num_msgs))
    #     if msgs_per_epoch <= 1:
    #         print("Not enough msgs in each epoch")
    #         exit(0)
        

    max_iterations = 100 
    # max_iterations = 5 
    non_bob_epochs = 1
    num_pop_users = 0
    num_other_senders = 0
    for msgs_per_epoch in range(0, 2001, 25):
        print("msgs_per_epoch_test: {}".format(msgs_per_epoch))
        # run_x_messages(msgs_per_epoch, num_users, max_iterations, num_epochs, msgs_mult, reply_mult, repeat_mult, "data/msgs_per_epoch_test_{:d}.dat".format(msgs_per_epoch), event_f, others_f)
        variant_3(msgs_per_epoch, num_users, max_iterations, non_bob_epochs, num_pop_users, num_other_senders, num_epochs, msgs_mult, reply_mult, repeat_mult, "data/msgs_per_epoch_test_variant_3_{:d}.dat".format(msgs_per_epoch), event_f, others_f)
    # run_updated_attack(msgs_per_epoch, num_users, max_iterations, 1, reply_mult, repeat_mult, "data/updated_attack_{:d}_{:d}.dat".format(1, num_users))
    # run_attack(msgs_per_epoch*3, num_users, max_iterations, 1, reply_mult, repeat_mult, 0.5, "data/old_attack_{:d}_{:d}".format(num_users, msgs_per_epoch*3), 1)

def alice_rank_test():
    # msgs_per_user_per_day = 50
    msgs_mult = 1
    reply_mult = 0.25
    repeat_mult = 0.25
    num_users = 10**6
    event_f = 0.00
    others_f = 0
    num_epochs = 100
    # msgs_per_epoch = ((msgs_per_user_per_day*num_users)/(24*60*60))
    msgs_per_epoch = 800

    max_iterations = 100 
    # max_iterations = 5 

    non_bob_epochs = 1
    num_pop_users = 0
    num_other_senders = 0

    print("Running Experiment 1: variant_3_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders))
    variant_3(msgs_per_epoch, num_users, max_iterations, non_bob_epochs, num_pop_users, num_other_senders, num_epochs, msgs_mult, reply_mult, repeat_mult, "data/variant_3_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders), event_f, others_f)

    num_pop_users = 1000 
    print("Running Experiment 2: variant_3_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders))
    variant_3(msgs_per_epoch, num_users, max_iterations, non_bob_epochs, num_pop_users, num_other_senders, num_epochs, msgs_mult, reply_mult, repeat_mult, "data/variant_3_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders), event_f, others_f)

    num_pop_users = 0
    num_other_senders = 5
    print("Running Experiment 3: variant_3_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders))
    variant_3(msgs_per_epoch, num_users, max_iterations, non_bob_epochs, num_pop_users, num_other_senders, num_epochs, msgs_mult, reply_mult, repeat_mult, "data/variant_3_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders), event_f, others_f)

    num_pop_users = 1000 
    num_other_senders = 5
    print("Running Experiment 4: variant_3_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders))
    variant_3(msgs_per_epoch, num_users, max_iterations, non_bob_epochs, num_pop_users, num_other_senders, num_epochs, msgs_mult, reply_mult, repeat_mult, "data/variant_3_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders), event_f, others_f)

    # num_pop_users = 1000 
    # print("Running Experiment 5: variant_2_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders))
    # variant_3(msgs_per_epoch, num_users, max_iterations, non_bob_epochs, num_pop_users, num_other_senders, num_epochs, msgs_mult, reply_mult, repeat_mult, "data/variant_2_{:d}_{:d}_{:d}.dat".format(msgs_per_epoch, num_pop_users, num_other_senders), event_f, others_f)


if __name__ == "__main__":
    # reply_repeat_fill_list_test()
    # reply_repeat_list_test()
    # reply_fill_list_test()
    # repeat_fill_list_test()
    # reply_list_test()
    # repeat_list_test()
    # fill_list_test()
    # repeat_percent_test()
    # multiple_senders_test()
    # message_rate_test()
    # updated_attack_test()
    # run_x_messages_test()
    # response_percentage_test()
    # rank_response_percentage_test()
    msgs_per_epoch_test()
    # alice_rank_test()
    # attack_variant_3()