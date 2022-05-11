from channels import *
from encoding import *
import numpy as np

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
