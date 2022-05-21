from channels import *
from encoding import *
from datagen import *


class Benchmark_runtime_params:
    def __init__(self, packet_size, noise_level):
        self.packet_size = packet_size
        self.noise_level = noise_level

class Benchmark:
    def __init__(
        self, 
        packet_limit, 
        retransmission_limit, 
        failure_ratio_threshold,
        unchecked_failure_ratio_period
        ):
        self.packet_limit = packet_limit
        self.retransmission_limit = retransmission_limit
        self.failure_ratio_threshold = failure_ratio_threshold
        self.unchecked_failure_ratio_period = unchecked_failure_ratio_period


    def bench(
        self,
        encoding_function,
        decoding_function, 
        channel_propagation_function,
        runtime_params,
        modify_runtime_params_function,
        runtime_params_period,
        description
        ):
        retransmission_limit_hits_since_params_change = 0
        packets_since_params_change = 0
        
        packet_idx = 0
        checksum_mismatch_count = 0
        checksum_collision_count = 0
        transmission_count = 0
        retransmission_limit_hit_count = 0

        collision_log_file = open(description+"_collisions.txt", 'w')
        csv_file = open(description+".csv", 'w')
        csv_file.write("packet_count;packet_size;noise_level;transmission_count;checksum_mismatch_count;checksum_collision_count;retransmission_limit_hit_count\n")

        def print_stats():
            stats = f'packet size: {runtime_params.packet_size}\n'\
                    f'noise level: {runtime_params.noise_level}\n'\
                    f'Transmitted: {transmission_count} packets\n'\
                    f'Checksum mismatches: {checksum_mismatch_count}\n'\
                    f'Checksum collisions: {checksum_collision_count}\n'\
                    f'Retransmission limit hits: {retransmission_limit_hit_count}\n'
            print(stats)
            csv_file.write(f'{packet_idx};{runtime_params.packet_size};{runtime_params.noise_level};{transmission_count};{checksum_mismatch_count};{checksum_collision_count};{retransmission_limit_hit_count}\n')

        while self.packet_limit == -1 or packet_idx < self.packet_limit:
            data = gen_data_packet(runtime_params.packet_size)
            encoded_packet = encoding_function(data)

            retransmission_count = 0
            while retransmission_count < self.retransmission_limit:
                propagated_packet = channel_propagation_function(encoded_packet, runtime_params.noise_level)
                transmission_count += 1
                ack, decoded_data = decoding_function(propagated_packet)

                if not ack:
                    checksum_mismatch_count += 1
                else:
                    if not np.array_equal(data, decoded_data):
                        checksum_collision_count += 1
                        collision_log_file.write(
                            f'sent:     {np.array2string(data, threshold=runtime_params.packet_size*8, separator="", max_line_width=runtime_params.packet_size*8+2)}\n'\
                            f'received: {np.array2string(decoded_data, threshold=runtime_params.packet_size*8, separator="", max_line_width=runtime_params.packet_size*8+2)}\n\n'
                        )
                    break

                retransmission_count += 1
            
            if retransmission_count == self.retransmission_limit:
                retransmission_limit_hit_count += 1
                retransmission_limit_hits_since_params_change += 1

            packet_idx += 1
            packets_since_params_change += 1

            if packet_idx % 100 == 0:
                print_stats()

            if (packets_since_params_change > self.unchecked_failure_ratio_period 
                and retransmission_limit_hits_since_params_change / packets_since_params_change > self.failure_ratio_threshold):
                break

            if packet_idx % runtime_params_period == 0:
                runtime_params = modify_runtime_params_function(runtime_params)
                retransmission_limit_hits_since_params_change = 0
                packets_since_params_change = 0
            
        
        print_stats()
        csv_file.close()
        collision_log_file.close()


benchmark = Benchmark(
    1e6, 
    10, 
    0.1,
    50
)

benchmark.bench(
    add_paritybit,
    verify_and_decode_parity, 
    bsc,
    Benchmark_runtime_params(8, 0.001),
    lambda params : Benchmark_runtime_params(params.packet_size*2, params.noise_level),
    1e3,
    "parity_bsc_increasing_packet_size"
)

benchmark.bench(
    add_paritybit,
    verify_and_decode_parity, 
    bsc,
    Benchmark_runtime_params(8, 0.001),
    lambda params : Benchmark_runtime_params(params.packet_size, params.noise_level*2),
    1e3,
    "parity_bsc_increasing_noise_level"
)


gilbert = Gilbert_channel(0, 0.5, 0.01, 0.4)


def gilbert_channel(data, noise_level):
    gilbert.bad_p = noise_level
    gilbert.good_to_bad_p = noise_level
    gilbert.bad_to_good_p = 1 - noise_level
    return gilbert.propagate(data)

benchmark.bench(
    add_crc32,
    verify_and_decode_crc32, 
    gilbert_channel,
    Benchmark_runtime_params(8, 0.001),
    lambda params : Benchmark_runtime_params(params.packet_size, params.noise_level*2),
    1e3,
    "crc32_gilbert_increasing_noise_level"
)