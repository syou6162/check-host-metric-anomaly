import sys
import os
import datetime
from sklearn.neighbors import LocalOutlierFactor
from sklearn.externals import joblib
from mackerel.clienthde import Client, MackerelClientError
from util import load_data, get_subseq_list

def get_lof(train, n_neighbors=20, contamination=0.01):
    # 学習データから怪しいものを抜く
    # lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.01)
    # train = np.delete(np.array(train), np.where(lof.fit_predict(np.array(train)) == -1)[0], axis=0)
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    lof.fit(train)
    return lof

def get_host_metrics(host_id, metric_name):
    client = Client(mackerel_api_key=os.environ["MACKEREL_APIKEY"])
    today = datetime.datetime.today()
    get_metrics = lambda from_, to: [m["value"] for m in client.get_host_metrics(host_id, metric_name, from_.strftime('%s'), to.strftime('%s'))["metrics"]]
    metrics = []
    try:
        metrics.extend(get_metrics(today + datetime.timedelta(days=-19), today + datetime.timedelta(days=-13)))
        metrics.extend(get_metrics(today + datetime.timedelta(days=-13), today + datetime.timedelta(days=-7)))
        metrics.extend(get_metrics(today + datetime.timedelta(days=-7), today + datetime.timedelta(hours=-12)))
        return metrics
    except MackerelClientError as e:
        return []

def main(args):
    host_id = args[0]
    metric_name = args[1]
    warning = float(args[2])
    critical = float(args[3])
    window_size = int(args[4])
    n_neighbors = int(args[5])

    model_prefix = "{}_{}_{}_{}_{}_{}".format(host_id, metric_name, warning, critical, window_size, n_neighbors)

    metrics = get_host_metrics(host_id, metric_name)
    if len(metrics) == 0:
        print("Failed to fetch host metrics from API")
        sys.exit(1)

    train = get_subseq_list(metrics, window_size=window_size)
    print("NUM_TRAIN: " + str(len(train)))

    lof_warning = get_lof(train, n_neighbors, warning)
    lof_critical = get_lof(train, n_neighbors, critical)
    models = {"warning": lof_warning, "critical": lof_critical}
    joblib.dump(models, "/tmp/" + model_prefix + '_lof.pkl')

if __name__ == '__main__':
    main(sys.argv[1:])
