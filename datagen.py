import random
import numpy as np


def gen_data_packet(bytes):
    data = np.empty(0, dtype=np.uint8)
    for i in range(bytes*8):
        data = np.append(data, random.randint(0, 1))
    return data
