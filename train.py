import sys
from sklearn.neighbors import LocalOutlierFactor
from sklearn.externals import joblib
from util import load_data, get_subseq_list

def get_lof(train, n_neighbors=20, contamination=0.01):
    # 学習データから怪しいものを抜く
    # lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.01)
    # train = np.delete(np.array(train), np.where(lof.fit_predict(np.array(train)) == -1)[0], axis=0)
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    lof.fit(train)
    return lof


def main(args):
    train_filename = args[0]
    model_prefix = args[1]
    warning = float(args[2])
    critical = float(args[3])
    window_size = int(args[4])
    n_neighbors = int(args[5])

    train = get_subseq_list(load_data(train_filename), window_size=window_size)
    print("NUM_TRAIN: " + str(len(train)))

    lof_warning = get_lof(train, n_neighbors, warning)
    lof_critical = get_lof(train, n_neighbors, critical)

    joblib.dump(lof_warning, "/tmp/" + model_prefix + '_warning_lof.pkl')
    joblib.dump(lof_critical, "/tmp/" + model_prefix + '_critical_lof.pkl')

if __name__ == '__main__':
    main(sys.argv[1:])
