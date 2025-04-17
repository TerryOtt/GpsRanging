import json

SV = {
   1: [2,6],
   2: [3,7],
   3: [4,8],
   4: [5,9],
   5: [1,9],
   6: [2,10],
   7: [1,8],
   8: [2,9],
   9: [3,10],
  10: [2,3],
  11: [3,4],
  12: [5,6],
  13: [6,7],
  14: [7,8],
  15: [8,9],
  16: [9,10],
  17: [1,4],
  18: [2,5],
  19: [3,6],
  20: [4,7],
  21: [5,8],
  22: [6,9],
  23: [1,3],
  24: [4,6],
  25: [5,7],
  26: [6,8],
  27: [7,9],
  28: [8,10],
  29: [1,6],
  30: [2,7],
  31: [3,8],
  32: [4,9],
}


def _gps_shift(register, feedback, output):
    """GPS Shift Register

    :param list feedback: which positions to use as feedback (1 indexed)
    :param list output: which positions are output (1 indexed)
    :returns output of shift register:

    """

    # calculate output
    out = [register[i - 1] for i in output]
    if len(out) > 1:
        out = sum(out) % 2
    else:
        out = out[0]

    # modulo 2 add feedback
    fb = sum([register[i - 1] for i in feedback]) % 2

    # shift to the right
    for i in reversed(range(len(register[1:]))):
        register[i + 1] = register[i]

    # put feedback in position 1
    register[0] = fb

    return out


def _gps_ca_prn(sv):
    """Build the CA code (PRN) for a given satellite ID

    :param int sv: satellite code (1-32)
    :returns list: ca code for chosen satellite

    """

    # init registers
    G1 = [1 for i in range(10)]
    G2 = [1 for i in range(10)]

    ca = []  # stuff output in here

    # create sequence
    for i in range(1023):
        g1 = _gps_shift(G1, [3, 10], [10])
        g2 = _gps_shift(G2, [2, 3, 6, 8, 9, 10], SV[sv])  # <- sat chosen here from table

        # modulo 2 add and append to the code
        ca.append((g1 + g2) % 2)

    # return C/A code!
    return ca

def _write_prns_to_json(computed_prns):
    """Write the CA codes (PRN) to JSON file

    :param list computed_prns: array of computed PRNs (each of which is is a list of ints)

    """
    # Create dictionary
    output_dict = {}
    for i in range(len(computed_prns)):
        output_dict[str(i + 1)] = computed_prns[i]

    with open("gps-ca-prns.json", "w") as json_file_handle:
        json.dump(output_dict, json_file_handle, indent=4, sort_keys=True)

def _main():
    computed_prns = []

    for i in range(1, 33):
        computed_prns.append(_gps_ca_prn(i))

    _write_prns_to_json(computed_prns)

if __name__ == "__main__":
    _main()