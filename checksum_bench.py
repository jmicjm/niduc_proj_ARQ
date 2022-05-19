from channels import *
from encoding import *
from datagen import *
from colors import *


def bench(
    encoding_function,
    decoding_function, 
    channel_propagation_function, 
    packet_limit, 
    initial_packet_size, 
    resize_period, 
    retransmission_limit, 
    failure_ratio_threshold,
    unchecked_failure_ratio_period,
    description):

    packet_size = initial_packet_size
    retransmission_limit_hits_since_size_change = 0
    packets_since_size_change = 0
    
    packet_idx = 0
    checksum_mismatch_count = 0
    checksum_collision_count = 0
    transmission_count = 0
    retransmission_limit_hit_count = 0

    csv_file = open(description+".csv", 'w').close()
    csv_file = open(description+".csv", 'a')
    csv_file.write("packet_count;packet_size;transmission_count;checksum_mismatch_count;checksum_collision_count;retransmission_limit_hit_count\n")

    def print_stats():
        stats = f'packet_size: {packet_size}\n'\
                f'Transmitted: {transmission_count} packets\n'\
                f'Checksum mismatches: {checksum_mismatch_count}\n'\
                f'Checksum collisions: {checksum_collision_count}\n'\
                f'Retransmission limit hits: {retransmission_limit_hit_count}\n'
        print(stats)
        csv_file.write(f'{packet_idx};{packet_size};{transmission_count};{checksum_mismatch_count};{checksum_collision_count};{retransmission_limit_hit_count}\n')

    while packet_limit == -1 or packet_idx < packet_limit:
        data = gen_data_packet(int(packet_size))
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
        
        if retransmission_count == retransmission_limit:
            retransmission_limit_hit_count += 1
            retransmission_limit_hits_since_size_change += 1

        packet_idx += 1
        packets_since_size_change += 1

        if packet_idx % 100 == 0:
            print_stats()

        if (packets_since_size_change > unchecked_failure_ratio_period 
            and retransmission_limit_hits_since_size_change / packets_since_size_change > failure_ratio_threshold):
            break

        if packet_idx % resize_period == 0:
            packet_size *= 2
            retransmission_limit_hits_since_size_change = 0
            packets_since_size_change = 0
        
    
    print_stats()
    csv_file.close()
