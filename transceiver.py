import threading
import queue

from channels import *
from encoding import *
from datagen import *


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def receiver_thread(data_queue, event, timeout, decoding_function, data_verif):
    while True:
        try:
            data = data_queue.get(True, timeout)
        except queue.Empty:
            print(
                bcolors.FAIL + "Receiver: Waiting for data timeout, returning..." + bcolors.ENDC)
            return

        result, data = decoding_function(data)
        if result:
            print(bcolors.OKCYAN + "Receiver: Correct data received..." + bcolors.ENDC)
            if np.array_equal(data_verif, data):
                print(bcolors.OKCYAN +
                      "Receiver: Data verification successful" + bcolors.ENDC)
            else:
                print(bcolors.FAIL +
                      "Receiver: Data verification failed" + bcolors.ENDC)

            event.set()
            return
        else:
            print(bcolors.OKCYAN + "Receiver: Received incorrect data" + bcolors.ENDC)


def transmitter_thread(data_queue, event, timeout, retry_count, data, encoding_function, channel_propagation_function):
    flag = False

    while flag != True and retry_count > 0:
        encoded_data = encoding_function(data)
        print(bcolors.WARNING + "Transmitter: sending data" + bcolors.ENDC)
        data_queue.put(channel_propagation_function(encoded_data))

        flag = event.wait(timeout)
        if flag:
            print(bcolors.WARNING + "Transmitter: got ACK" + bcolors.ENDC)
        else:
            print(bcolors.WARNING + "Transmitter: NACK, resend..." + bcolors.ENDC)
            retry_count -= 1
    if retry_count == 0:
        print(bcolors.FAIL +
              "Transmitter: Too many retries, channel is unusable, exiting" + bcolors.ENDC)


def init_transaction(encoding_function, decoding_function, channel_propagation_function):
    data = gen_data_packet(10)
    data_queue = queue.Queue()

    event = threading.Event()
    trans_thread = threading.Thread(
        target=transmitter_thread, args=(data_queue, event, 1, 10, data, encoding_function, channel_propagation_function))
    recv_thread = threading.Thread(
        target=receiver_thread, args=(data_queue, event, 2, decoding_function, data))

    recv_thread.start()
    trans_thread.start()
