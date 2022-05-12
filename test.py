import numpy as np

from channels import *
from encoding import *
from datagen import *
from transceiver import *

data = np.array([0, 0, 0, 1, 1, 1, 1, 0])
print("data   ", data)
print("bec    ", bec(data, 0.2))
print("bsc    ", bsc(data, 0.2))
print("gilbert", Gilbert_channel(0, 0.5, 0.2, 0.2).propagate(data))
print("parity ", gen_paritybit(data))
print("crc32  ", gen_crc32(data))
print("parity ", add_paritybit(data))
print("crc32  ", add_crc32(data))
print("doubling       ", add_doubling(data))
print("crc32 verif    ", verify_and_decode_crc32(add_crc32(data)))
print("parity verif   ", verify_and_decode_parity(add_paritybit(data)))
print("doubling verif ", verify_and_decode_doubling(add_doubling(data)))
wrong_crc32 = add_crc32(data)
wrong_crc32[-1] = 0
print("crc32 verif w  ", verify_and_decode_crc32(wrong_crc32))
wrong_parity = add_paritybit(data)
wrong_parity[-1] = 1
print("parity verif w ", verify_and_decode_parity(wrong_parity))
wrong_doubling = add_doubling(data)
wrong_doubling[-1] = 1
print("doubling verif ", verify_and_decode_doubling(wrong_doubling))
print("random data pa ", gen_data_packet(2))

print("===transceiver test===")

def bsc_channel(data):
    return bsc(data, 0.01)


def bec_channel(data):
    return bec(data, 0.01)


gilbert = Gilbert_channel(0, 0.5, 0.01, 0.4)


def gilbert_channel(data):
    return gilbert.propagate(data)

transceiver  = Transceiver(
    Transmitter_params(add_crc32, 1, 10),
    Receiver_params(verify_and_decode_crc32, 10),
    bec_channel
    )

packet_count = 16
stats = transceiver.init_transaction(10, packet_count)

print("tried to sent: ", packet_count, " packets")
print("received_correct: ", stats.received_correct(), " packets")
print("received incorrect: ", stats.received_incorrect, " packets")
print("verification successfull: ", stats.verification_successfull, " packets")
print("verification unsuccessfull: ", stats.verification_unsuccessfull, " packets")
