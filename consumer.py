import time
import zmq
import random


def consumer():
    consumer_id = random.randrange(1,10005)
    print (f"I am consumer {consumer_id}")
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:5557")

    while True:
        work = consumer_receiver.recv_string()
        print(f"got a work {work}")


consumer()

