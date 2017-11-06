# check-host-metric-anomaly
Mackerelのホストメトリックの異常検知を行なうチェック監視プラグインです。

# 概要
- 異常検知の代表的なアルゴリズムの一つである[LOF(Local Outlier Factor)](https://en.wikipedia.org/wiki/Local_outlier_factor)を利用しています
  - 大雑把には「自分の近傍にデータ点が少ないデータほど異常である」という[k近傍法](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm)的な考え方のアルゴリズムです
- ホストメトリックの時系列的な異常検知を行なえます
  - 1次元の時系列データをwindow幅(D)で区切ってD次元ベクトルに変換後、LOFに投げます
  - データを取得しているMackerelのAPIのエンドポイントを変えれば簡単にサービスメトリックに対しても動かせるようになるはず
- モニタリング専用のホストで動かすのがオススメです
  - アルゴリズムの学習と異常検知をagentを動かしているホスト内で行なうので、多少負荷がかかります

# Install/Build
scikit-learnを利用していますが、環境を手元で作ってもらう手間を省くためにdockerを経由して動かします。

手元で動かせるDockerイメージをDocker Hubで[ホスト](https://hub.docker.com/r/yasuhisa/check-host-metric-anomaly/)しています。Dockerが手元で動く環境であれば、以下のコマンドで使えるようになります。

```
% docker pull yasuhisa/check-host-metric-anomaly
```

修正を加えて手元でbuildすることもできます。

```
% docker build -t yasuhisa/check-host-metric-anomaly .
```

# mackerel-agent.confの書き方例
- 学習データや異常検知をする直近のデータ取得のため、MackerelのAPIKEYが必要です
- HOST_ID(例: `2GyUJSydbQq`)には収集したいホストidを記述してください
- METRIC_NAME(例: `loadavg5`や`cpu.user.percentage`など)には収集したいメトリック名を記述してください
  - カスタムメトリックも指定できます
  - ワイルドカード指定は今のところできません
- `max_check_attempts`はなくてもよいですが、時々タイムアウトでUNKNOWNになってしまうため、付けておいたほうが安心です

```conf
[plugin.checks.anomaly_sample]
command = "/path/to/docker run --rm -e MACKEREL_APIKEY=XXXXX -v /tmp:/tmp yasuhisa/check-host-metric-anomaly /app/run.sh --host-id HOST_ID --metric-name METRIC_NAME"
max_check_attempts = 3
```

たくさんのホストメトリックを監視する場合、`docker run`ではコンテナの起動/停止の負荷が大きくなります。その場合にはagentの起動前に`docker start`しておいて、`docker run`の代わりに`docker exec`を使うのがお勧めです。

```sh
% docker run -d --name check-host-metric-anomaly -e MACKEREL_APIKEY=XXXXX -v /tmp:/tmp yasuhisa/check-host-metric-anomaly init
% docker start check-host-metric-anomaly
```

```conf
[plugin.checks.anomaly_sample]
command = "/path/to/docker exec check-host-metric-anomaly /app/run.sh --host-id HOST_ID --metric-name METRIC_NAME"
max_check_attempts = 3
```
