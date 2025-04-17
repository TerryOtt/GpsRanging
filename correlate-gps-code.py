import json
import random


def _load_gps_ca_prns():
    with open("gps-ca-prns.json") as json_file:
        gps_ca_prns = json.load(json_file)
    return gps_ca_prns


def _first_last_eight(prn):

    print(f"PRN: {prn}")
    return_str = ""
    for i in range(8):
        return_str += str(prn[i])
        if i == 3:
            return_str += " "

    return_str += " ... "

    for i in range(-8, 0):
        return_str += str(prn[i])
        if i == -5:
            return_str += " "

    return return_str


def _rotate_shift_prn(prn, bits_to_shift):
    #print(f"Shifting PRN by {bits_to_shift} bits")
    if bits_to_shift == 0:
        return prn

    tail_bits = prn[-bits_to_shift:]

    #print(f"Tail bits: {tail_bits}")
    front_bits = prn[0:-(bits_to_shift + 1)]
    shifted_prn = tail_bits + front_bits
    return shifted_prn


def _create_shifted_versions(curr_prn):
    shifted_versions = [curr_prn, ]

    for i in range(1, 1023):
        shifted_prn = _rotate_shift_prn(curr_prn, i)
        #print(f"Shifted PRN: {shifted_prn}")
        shifted_versions.append(shifted_prn)

    return shifted_versions


def _create_unique_prefixes(shifted_prn_list):
    shifted_versions_with_this_prefix = {}
    unique_prefixes = {}
    for (shift_list_idx, curr_shifted_version) in enumerate(shifted_prn_list):
        #print(f"curr shifted version: {curr_shifted_version}")
        # Walk through bits and generate counts for each prefix version until we get a unique one
        for bit_idx in range(len(curr_shifted_version)):
            # What's our list look like at this point:
            curr_bit_prefix_list = curr_shifted_version[:bit_idx + 1]

            # Do we already know how many shifted versions start with this list
            string_version_of_list = str(curr_bit_prefix_list)
            #print(f"\tCurr bit prefix list for length {bit_idx + 1}: {string_version_of_list}")
            if string_version_of_list in shifted_versions_with_this_prefix:
                #print(f"\tNumber of shifted version with this prefix: {shifted_versions_with_this_prefix[string_version_of_list]} (found in prefix list)")
                continue
            else:
                # This may be a unique prefix, let's walk from our index down and find out
                shifted_versions_with_this_prefix[string_version_of_list] = 1
                for shifted_version_search_idx in range(shift_list_idx + 1, len(shifted_prn_list)):
                    if str(shifted_prn_list[shifted_version_search_idx][:bit_idx + 1]) == string_version_of_list:
                        shifted_versions_with_this_prefix[string_version_of_list] += 1

                # If there's only one version of this prefix, it's unique, let's register it
                if shifted_versions_with_this_prefix[string_version_of_list] == 1:
                    unique_prefixes[string_version_of_list] = {
                        "prn_index": 1,
                        "prn_rotate_bits": shift_list_idx,
                        "full_bit_string": str(curr_shifted_version),
                    }

                    # No more work to do for this prefix
                    break

    #print(f"Prefix counts: \n{json.dumps(shifted_versions_with_this_prefix, indent=4, sort_keys=True)}")
    #print("unique prefixes:\n" + json.dumps(unique_prefixes, indent=4, sort_keys=True))

    return unique_prefixes


def _main():
    ca_prns = _load_gps_ca_prns()
    #print(f"CA 1: {ca_prns['1']}")
    #print("Offset 0: " + _first_last_eight(curr_prn))
    curr_ca = 1
    curr_prn = ca_prns[str(curr_ca)]
    shifted_prn_list = _create_shifted_versions(curr_prn)

    unique_prefixes = _create_unique_prefixes(shifted_prn_list)
    print(f"Number of unique prefixes: {len(unique_prefixes)}")

    # Find shortest prefix in the list of unique prefixes, so we don't waste time searching below that
    shortest_prefix = 1023
    for curr_prefix in unique_prefixes:
        curr_unique_prefix_entry = unique_prefixes[curr_prefix]
        unique_prefix_list = json.loads(curr_prefix)
        if len(unique_prefix_list) < shortest_prefix:
            shortest_prefix = len(unique_prefix_list)

    print(f"Shortest unique prefix is {shortest_prefix} bits long")

    # Do a test

    # Pick a shifted PRN at random
    random_correlation_offset = random.randint(1, len(shifted_prn_list))
    print(f"Picked random code correlation offset (bits): {random_correlation_offset}")

    # How many bits of our rotated string do we need to walk through to find out which version it is?
    full_search_bit_string = shifted_prn_list[random_correlation_offset]
    #print(f"Full search bit string: {full_search_bit_string}")

    for search_bit_index in range(shortest_prefix, len(full_search_bit_string)+1):
        search_string = str(full_search_bit_string[:search_bit_index])
        #print(f"\tSearch substring ({search_bit_index} bits): {search_string}")

        if search_string in unique_prefixes:
            matched_unique_prefix = unique_prefixes[search_string]
            print(f"Found search string in unique prefix list at bit index {search_bit_index}!")
            print(f"\tPRN index: {matched_unique_prefix['prn_index']}")
            code_correlation_offset_bits = matched_unique_prefix['prn_rotate_bits']
            print(f"\tPRN code correlation offset: {code_correlation_offset_bits} bits")

            # Calculate code correlation in seconds
            seconds_per_ca_bit = 1 / float(1023 * 1000)
            code_correlation_seconds = float(code_correlation_offset_bits) * seconds_per_ca_bit
            print(f"\tPRN code correlation offset: {code_correlation_seconds:9.07f} s")
            speed_of_light_m_per_s = 299792458
            sv_pseudorange_meters = speed_of_light_m_per_s * code_correlation_seconds
            print(f"\tPseudorange:")
            print(f"\t\t Minimum: {seconds_per_ca_bit * speed_of_light_m_per_s:9.02f} m")
            print(f"\t\tComputed: {sv_pseudorange_meters:9.02f} m  (GPS satellite altitude: 20200.00 m)")
            print(f"\t\t Maximum: {1023 * seconds_per_ca_bit * speed_of_light_m_per_s:9.02f} m")

            break


if __name__ == "__main__":
    _main()