import numpy as np

from channels import *
from encoding import *
from datagen import *
from transceiver import *
from colors import *
from checksum_bench import *

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


bench(add_paritybit, verify_and_decode_parity, bsc_channel, 1e3, 32, 10, "parity.txt")
bench(add_doubling, verify_and_decode_doubling, bsc_channel, 1e3, 32, 10, "doubling.txt")
bench(add_crc32, verify_and_decode_crc32, bsc_channel, -1, 32, 10, "crc32.txt")


transceiver = Transceiver(
    Transmitter_params(add_crc32, 1, 10),
    Receiver_params(verify_and_decode_crc32, 2),
    bec_channel
)

packet_count = 16
stats = transceiver.init_transaction(10, packet_count)

stats.print()
