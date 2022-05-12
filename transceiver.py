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


class Receiver_params:
    def __init__(self, decoding_function, timeout):
        self.decoding_function = decoding_function
        self.timeout = timeout

def receiver_thread(params, data_queue, event, data_verif):
    while True:
        try:
            data = data_queue.get(True, params.timeout)
        except queue.Empty:
            print(
                bcolors.FAIL + "Receiver: Waiting for data timeout, returning..." + bcolors.ENDC)
            return

        result, data = params.decoding_function(data)
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


class Transmitter_params:
    def __init__(self, encoding_function, timeout, retry_count):
        self.encoding_function = encoding_function
        self.timeout = timeout
        self.retry_count = retry_count

def transmitter_thread(params, data_queue, event, data, channel_propagation_function):
    flag = False

    while flag != True and params.retry_count > 0:
        encoded_data = params.encoding_function(data)
        print(bcolors.WARNING + "Transmitter: sending data" + bcolors.ENDC)
        data_queue.put(channel_propagation_function(encoded_data))

        flag = event.wait(params.timeout)
        if flag:
            print(bcolors.WARNING + "Transmitter: got ACK" + bcolors.ENDC)
        else:
            print(bcolors.WARNING + "Transmitter: NACK, resend..." + bcolors.ENDC)
            params.retry_count -= 1
    if params.retry_count == 0:
        print(bcolors.FAIL +
              "Transmitter: Too many retries, channel is unusable, exiting" + bcolors.ENDC)


class Transceiver:
    def __init__(self, transmitter_params, receiver_params, channel_propagation_function, packet_size):
        self.transmitter_params = transmitter_params
        self.receiver_params = receiver_params
        self.channel_propagation_function = channel_propagation_function
        self.packet_size = packet_size

    def init_transaction(self):
        data = gen_data_packet(self.packet_size)
        data_queue = queue.Queue()

        event = threading.Event()
        trans_thread = threading.Thread(
            target=transmitter_thread, args=(self.transmitter_params, data_queue, event,  data, self.channel_propagation_function))
        recv_thread = threading.Thread(
            target=receiver_thread, args=(self.receiver_params, data_queue, event,  data))

        recv_thread.start()
        trans_thread.start()

        recv_thread.join()
        trans_thread.join()
