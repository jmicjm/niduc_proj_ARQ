import threading
import time
import queue

from channels import *
from encoding import *
from datagen import *


def receiver_thread(data_queue, event, decoding_function):
    while True:
        try:
            data = data_queue.get(True, 1)
        except queue.Empty:
            print("Queue is empty, returning...")
            return

        result, data = decoding_function(data)
        if result:
            event.set()
            print("Received correct data:")
            print(data)
            return
        else:
            print("Received incorrect data")


def transmitter_thread(data_queue, event, timeout, retry_count, data, encoding_function, channel_propagation_function):
    flag = False

    while flag != True and retry_count > 0:
        encoded_data=encoding_function(data)
        data_queue.put(channel_propagation_function(encoded_data))

        flag = event.wait(timeout)
        if flag:
            print("ACK")
        else:
            print("Transmission error, resend...")
            retry_count -= 1


def init_transaction(encoding_function, decoding_function, channel_propagation_function):
    data = gen_data_packet(10)
    data_queue = queue.Queue()

    event = threading.Event()
    trans_thread = threading.Thread(
        target=transmitter_thread, args=(data_queue, event, 1, 10, data, encoding_function, channel_propagation_function))
    recv_thread = threading.Thread(
        target=receiver_thread, args=(data_queue, event, decoding_function))

    recv_thread.start()
    trans_thread.start()
