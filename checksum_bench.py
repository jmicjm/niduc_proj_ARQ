from channels import *
from encoding import *
from datagen import *
from colors import *

#-1 packet_limit - infinite execution
def bench(encoding_function, decoding_function, channel_propagation_function, packet_limit, packet_size, retransmission_limit, filename):
    packet_idx = 0
    checksum_mismatch_count = 0
    checksum_collision_count = 0
    transmission_count = 0
    retransmission_limit_hit_count = 0

    def print_stats():
        stats = f'Transmitted: {transmission_count} packets\n'\
                f'Checksum mismatches: {checksum_mismatch_count}\n'\
                f'Checksum collisions: {checksum_collision_count}\n'\
                f'Retransmission limit hits: {retransmission_limit_hit_count}\n'
        file = open(filename, 'w')
        file.write(stats)
        file.close()
        print(f'following lines were saved to {filename}:\n'+stats)

    while packet_limit == -1 or packet_idx < packet_limit:
        data = gen_data_packet(packet_size)
        encoded_packet = encoding_function(data)

        retransmission_count = 0
        while retransmission_count < retransmission_limit:
            propagated_packet = channel_propagation_function(encoded_packet)
            transmission_count += 1
            ack, decoded_data = decoding_function(propagated_packet)

            if not ack:
                checksum_mismatch_count += 1
            else:
                if not np.array_equal(data, decoded_data):
                    checksum_collision_count += 1
                break

            retransmission_count += 1

            if transmission_count % 50000 == 0:
                print_stats()
        
        if retransmission_count == retransmission_limit:
            retransmission_limit_hit_count += 1

        packet_idx += 1
    
    print_stats()
