import numpy as np
import random
import commpy.channels as chan


def bec(input_data, p):
    output_data = chan.bec(input_data, p)
    return np.delete(output_data, np.where(output_data == -1))

def bsc(input_data, p):
    return chan.bsc(input_data, p)

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