from colors import *

class Transaction_stats:
    received_incorrect = 0
    verification_successfull = 0
    verification_unsuccessfull = 0

    def received_correct(self):
        return self.verification_successfull + self.verification_unsuccessfull

    def print(self):
        print(bcolors.OKGREEN + "Stats: Sent: ",
              self.received_incorrect + self.received_correct(), " packets")
        print("Stats:   - Received correct: ",
              self.received_correct(), " packets")
        print("Stats:   - Received incorrect: ",
              self.received_incorrect, " packets")
        print("Stats: Verification successfull: ",
              self.verification_successfull, " packets")
        print("Stats: Verification unsuccessfull: ",
              self.verification_unsuccessfull, " packets" + bcolors.ENDC)
