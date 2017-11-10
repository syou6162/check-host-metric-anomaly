import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from sklearn.externals import joblib
from mackerel.clienthde import Client, MackerelClientError
from util import load_data, get_subseq_list
plt.switch_backend('agg')


def get_predictions(lof, test):
    result = lof._predict(test)
    print(result[-10:])
    return result


def plot_result(filename, test_average, result, window_size):
    plt.plot(test_average)
    alert_idx = list(map(lambda n: n + window_size - 1, np.where(result == -1)[0]))
    plt.scatter(alert_idx, pd.Series(test_average)[alert_idx], color="red")
    plt.savefig("/tmp/" + filename)
    plt.close()

def get_host_metrics(host_id, metric_name):
    client = Client(mackerel_api_key=os.environ["MACKEREL_APIKEY"])
    today = datetime.datetime.today()
    from_ = today + datetime.timedelta(hours=-12)
    return [m["value"] for m in client.get_host_metrics(host_id, metric_name, from_.strftime('%s'), today.strftime('%s'))["metrics"]]

def main(args):
    host_id = args[0]
    metric_name = args[1]
    model_filename = args[2]
    window_size = int(args[3])

    # 学習データは5分粒度なので、テストデータも1分粒度のものを5分の平均に丸める
    test_average = list(map(lambda l: np.mean(l), get_subseq_list(get_host_metrics(host_id, metric_name), window_size=5)))[::5]
    test = get_subseq_list(test_average, window_size=window_size)

    try:
        models = joblib.load(model_filename)
    except FileNotFoundError:
       sys.exit(3)

    warning_results = get_predictions(models["warning"], test)
    critical_results = get_predictions(models["critical"], test)

    warning_result_filename = "result_warning.png"
    critical_result_filename = "result_critical.png"
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
