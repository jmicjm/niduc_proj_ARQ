import binascii
import numpy as np
import random
import commpy.channels as chan


def bec(input_data, p):
    output_data = chan.bec(input_data, p)
    return np.delete(output_data, np.where(output_data == -1))

def bsc(input_data, p):
    return chan.bsc(input_data, p)

def gen_crc32(input_data):
    return binascii.crc32(input_data)

def gen_paritybit(input_8bit):
    ones_count = 0
    for i in range(8):
        ones_count += input_8bit[i]
    return ones_count % 2

def add_crc32(input_data):
    crc32 = gen_crc32(input_data)
    return np.append(input_data, [int(x) for x in bin(crc32)[2:]])

def add_paritybit(input_data):
    output_data = np.empty(0,dtype=np.uint8)
    for i in range(input_data.size // 8):
        arr = input_data[i*8:i*8+8]
        bit = gen_paritybit(arr)
        output_data = np.append(output_data, arr)
        output_data = np.append(output_data, bit)
    return output_data

def add_doubling(input_data):
    return np.append(input_data, input_data)

class Gilbert_channel:
    good = True

    def __init__(self, good_p, bad_p, good_to_bad_p, bad_to_good_p):
         self.good_p = good_p
         self.bad_p = bad_p
         self.good_to_bad_p = good_to_bad_p
         self.bad_to_good_p = bad_to_good_p

    def change_state(self):
        self.good = self.good ^ (random.uniform(0,1) <= (self.good_to_bad_p if self.good else self.bad_to_good_p))            

    def propagate(self, input_data):
        output_data = input_data.copy()
        for i in range(output_data.size):
            self.change_state()
            output_data[i] = output_data[i] ^ (random.uniform(0,1) <= (self.good_p if self.good else self.bad_p))
        return output_data