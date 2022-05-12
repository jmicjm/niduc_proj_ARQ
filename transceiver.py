import threading
import time
import queue

from channels import *
from encoding import *
from datagen import *


def receiver_thread(data_queue, event):
    while True:
        try:
            data = data_queue.get(True, 1)
        except queue.Empty:
            print("Queue is empty, returning...")
            return

        result, data = verify_and_decode_crc32(data)
        if result:
            event.set()
            print("Received correct data:")
            print(data)
            return
        else:
            print("Received incorrect data")


def transmitter_thread(data_queue, event, timeout, retry_count, encoded_data):
    flag = False

    while flag != True and retry_count > 0:
        data_queue.put(encoded_data)

        flag = event.wait(timeout)
        if flag:
            print("ACK")
        else:
            print("Transmission error, resend...")
            retry_count -= 1


def init_transaction():
    data = gen_data_packet(10)
    encoded_data = add_crc32(data)
    data_queue = queue.Queue()

    event = threading.Event()
    trans_thread = threading.Thread(
        target=transmitter_thread, args=(data_queue, event, 1, 10, encoded_data))
    recv_thread = threading.Thread(
        target=receiver_thread, args=(data_queue, event))

    recv_thread.start()
    trans_thread.start()


init_transaction()
