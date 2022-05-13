from colors import *

class Transaction_stats:
    received_incorrect = 0
    verification_successfull = 0
    verification_unsuccessfull = 0

    def received_correct(self):
        return self.verification_successfull + self.verification_unsuccessfull

    def print(self, expected_correct_count):
        print(bcolors.OKGREEN + "Stats: Sent: ",
              self.received_incorrect + self.received_correct(), " packets")
        r_correct_color = bcolors.OKGREEN if self.received_correct() == expected_correct_count else bcolors.FAIL
        print(r_correct_color + "Stats:   - Received correct: ",
              self.received_correct(), " packets")
        print(bcolors.OKGREEN + "Stats:   - Received incorrect: ",
              self.received_incorrect, " packets")
        print("Stats: Verification successfull: ",
              self.verification_successfull, " packets")
        v_successfull_color = bcolors.OKGREEN if self.verification_unsuccessfull == 0 else bcolors.FAIL
        print(v_successfull_color + "Stats: Verification unsuccessfull: ",
              self.verification_unsuccessfull, " packets" + bcolors.ENDC)
