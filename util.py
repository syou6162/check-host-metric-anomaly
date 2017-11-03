def load_data(filename):
    data = []
    with open(filename, 'r') as fh:
        for line in fh:
            data.append(float(line.strip()))
    return data


def _subseq_list(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])


def get_subseq_list(data, window_size=20):
    return list(map(lambda l: list(l), _subseq_list(data, window_size)))

