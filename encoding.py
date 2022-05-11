from bitarray.util import ba2int
import binascii
import numpy as np

empty_array = np.empty(0,dtype=np.uint8)

def gen_crc32(input_data):
    return binascii.crc32(input_data)

def gen_paritybit(input_8bit):
    ones_count = 0
    for i in range(8):
        ones_count += input_8bit[i]
    return ones_count % 2

def int_to_bin(input_data):
    return np.array([int(x) for x in bin(input_data)[2:]])

def add_crc32(input_data):
    crc32 = int_to_bin(gen_crc32(input_data))
    align_to_32bits = np.zeros(32-crc32.size,dtype=np.uint8)
    crc32 = np.concatenate((align_to_32bits,crc32))
    return np.append(input_data, crc32)

def add_paritybit(input_data):
    output_data = empty_array
    for i in range(0, input_data.size, 8):
        arr = input_data[i:i+8]
        bit = gen_paritybit(arr)
        output_data = np.append(output_data, arr)
        output_data = np.append(output_data, bit)
    return output_data

def add_doubling(input_data):
    output_data = empty_array
    for i in range(input_data.size):
        output_data = np.append(output_data, [input_data[i],input_data[i]])
    return output_data

def bit_arr_to_int(arr):
    mult=0
    val=0
    for i in range(arr.size-1,-1,-1):
        val+= pow(2, mult) * arr[i]
        mult+=1
    return val

def verify_and_decode_crc32(input_data):
    data_wo_checksum = input_data[:-32]
    checksum = input_data[-32:]
    if gen_crc32(data_wo_checksum) == bit_arr_to_int(checksum):
        return True, data_wo_checksum
    else:
        return False, empty_array

def verify_and_decode_parity(input_data):
    output_data = empty_array
    for i in range(0, input_data.size, 9):
        data=input_data[i:i+8]
        parity = input_data[i+8]
        if gen_paritybit(data) != parity:
            return False, empty_array
        output_data=np.append(output_data,data)
    return True, output_data

def verify_and_decode_doubling(input_data):
    if input_data.size % 2 != 0:
        return False, empty_array
    
    output_data = empty_array
    for i in range(0, input_data.size, 2):
        if input_data[i] != input_data[i+1]:
            return False, empty_array
        else:
            output_data = np.append(output_data, input_data[i])

    return True, output_data