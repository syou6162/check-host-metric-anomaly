import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from util import load_data, get_subseq_list
plt.switch_backend('agg')


def get_predictions(train, test, contamination=0.01, n_neighbors=20):
    # 学習データから怪しいものを抜く
    # lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.01)
    # train = np.delete(np.array(train), np.where(lof.fit_predict(np.array(train)) == -1)[0], axis=0)

    lof = get_lof(train, contamination=contamination, n_neighbors=n_neighbors)
    result = lof._predict(test)
    print(result[-10:])
    return result


def plot_result(filename, test_average, result, window_size):
    plt.plot(test_average)
    alert_idx = list(map(lambda n: n + window_size - 1, np.where(result == -1)[0]))
    plt.scatter(alert_idx, pd.Series(test_average)[alert_idx], color="red")
    plt.savefig("/tmp/" + filename)
    plt.close()


def main(args):
    train_filename = args[0]
    test_filename = args[1]
    warning = float(args[2])
    critical = float(args[3])
    window_size = int(args[4])
    n_neighbors = int(args[5])

    train = get_subseq_list(load_data(train_filename), window_size=window_size)
    # 学習データは5分粒度なので、テストデータも1分粒度のものを5分の平均に丸める
    test_average = list(map(lambda l: np.mean(l), get_subseq_list(load_data(test_filename), window_size=5)))[::5]
    test = get_subseq_list(test_average, window_size=window_size)

    print("NUM_TRAIN: " + str(len(train)))

    warning_results = get_predictions(train, test, contamination=warning, n_neighbors=n_neighbors)
    critical_results = get_predictions(train, test, contamination=critical, n_neighbors=n_neighbors)

    warning_result_filename = "result_warning_" + str(warning) + ".png"
    critical_result_filename = "result_critical_" + str(critical) + ".png"
    plot_result(warning_result_filename, test_average, warning_results, window_size)
    plot_result(critical_result_filename, test_average, critical_results, window_size)

    if critical_results[-1] == -1:
        sys.exit(2)
    elif warning_results[-1] == -1:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
