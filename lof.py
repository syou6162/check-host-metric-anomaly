import sys
from sklearn.neighbors import LocalOutlierFactor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')

def load_data(filename):
    data = []
    with open(filename, 'r') as fh:
        for line in fh:
            data.append(float(line.strip()))
    return data

def _subseq_list(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])

def get_subseq_list(data, window_size = 20):
    return list(map(lambda l: list(l), _subseq_list(data, window_size)))

def get_lof(train, n_neighbors=20, contamination=0.01):
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    lof.fit(train)
    return lof
 
def get_predict(lof, test):
    return lof._predict(test)

def plot_result(train, test, test_average, window_size = 20, contamination=0.01, n_neighbors=20):
    # 学習データから怪しいものを抜く
    # lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.01)
    # train = np.delete(np.array(train), np.where(lof.fit_predict(np.array(train)) == -1)[0], axis=0)

    lof = get_lof(train, contamination=contamination, n_neighbors=n_neighbors)
    result = get_predict(lof, test)
    print(result[-10:])

    plt.plot(test_average)
    alert_idx = list(map(lambda n: n + window_size - 1, np.where(result == -1)[0]))
    plt.scatter(alert_idx, pd.Series(test_average)[alert_idx], color="red")
    plt.savefig("/tmp/" + str(contamination) + "hoge.png")
    plt.close()
    return result[-1]

train_filename = sys.argv[1]
test_filename = sys.argv[2]
window_size = 5
n_neighbors = 20

train = get_subseq_list(load_data(train_filename), window_size=window_size)
print(len(train))
# 学習データは5分粒度なので、テストデータも1分粒度のものを5分の平均に丸める
test_average = list(map(lambda l: np.mean(l), get_subseq_list(load_data(test_filename), window_size=5)))[::5]
test = get_subseq_list(test_average, window_size=window_size)

warning_result = plot_result(train, test, test_average, window_size = window_size, contamination = 0.005, n_neighbors = n_neighbors)
critical_result = plot_result(train, test, test_average, window_size = window_size, contamination = 0.001, n_neighbors = n_neighbors)

if critical_result == -1:
    sys.exit(2)
elif warning_result == -1:
    sys.exit(1)
else:
    sys.exit(0)
