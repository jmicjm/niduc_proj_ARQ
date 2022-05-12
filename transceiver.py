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


class Validator:
    def __init__(self, original_data):
        self.original_data = original_data
    
    def validate(self, data):
        if np.array_equal(self.original_data, data):
            print(bcolors.OKCYAN +
                    "Validator: Data verification successful" + bcolors.OKGREEN)
            return True
        else:
            print(bcolors.FAIL +
                    "Validator: Data verification failed" + bcolors.FAIL)
            return False

class Transaction_stats:
    received_incorrect = 0
    verification_successfull = 0
    verification_unsuccessfull = 0

    def received_correct(self):
        return self.verification_successfull + self.verification_unsuccessfull

class Receiver_params:
    def __init__(self, decoding_function, timeout):
        self.decoding_function = decoding_function
        self.timeout = timeout

def receiver_thread(params, data_queue, event, verificator, stats):
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

            if verificator.validate(data):
                stats.verification_successfull += 1
            else:
                stats.verification_unsuccessfull += 1

            event.set()
            return
        else:
            print(bcolors.OKCYAN + "Receiver: Received incorrect data" + bcolors.ENDC)
            stats.received_incorrect += 1

class Transmitter_params:
    def __init__(self, encoding_function, timeout, retry_count):
        self.encoding_function = encoding_function
        self.timeout = timeout
        self.retry_count = retry_count

def transmitter_thread(params, data_queue, event, data, channel_propagation_function):
    flag = False
    retry_count = params.retry_count

    while flag != True and retry_count > 0:
        encoded_data = params.encoding_function(data)
        print(bcolors.WARNING + "Transmitter: sending data" + bcolors.ENDC)
        data_queue.put(channel_propagation_function(encoded_data))

        flag = event.wait(params.timeout)
        if flag:
            print(bcolors.WARNING + "Transmitter: got ACK" + bcolors.ENDC)
        else:
            print(bcolors.WARNING + "Transmitter: NACK, resend..." + bcolors.ENDC)
            retry_count -= 1
    if retry_count == 0:
        print(bcolors.FAIL +
              "Transmitter: Too many retries, channel is unusable, exiting" + bcolors.ENDC)


class Transceiver:
    def __init__(self, transmitter_params, receiver_params, channel_propagation_function):
        self.transmitter_params = transmitter_params
        self.receiver_params = receiver_params
        self.channel_propagation_function = channel_propagation_function

    def init_transaction(self, packet_size, packet_count):
        stats = Transaction_stats()
        data_queue = queue.Queue()

        for i in range(packet_count):
            data = gen_data_packet(packet_size)
            validator = Validator(data)

            event = threading.Event()
            trans_thread = threading.Thread(
                target=transmitter_thread, args=(self.transmitter_params, data_queue, event,  data, self.channel_propagation_function))
            recv_thread = threading.Thread(
                target=receiver_thread, args=(self.receiver_params, data_queue, event, validator, stats))

            recv_thread.start()
            trans_thread.start()

            recv_thread.join()
            trans_thread.join()

        return stats
