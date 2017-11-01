# mackerel_ts_anomaly_detection
check監視を使ってホストメトリックの異常検知を行ないます。異常検知の代表的なアルゴリズムの一つであるLOF(Local Outlier Factor)を利用しています。

# Build
scikit-learnを利用していますが、環境を手元で作ってもらう手間を省くためにdockerを経由して動かします。

```
% docker build -t yasuhisa/mackerel_ts_anomaly_detection .
```

# mackerel-agent.confの書き方例
- 学習データや異常検知をする直近のデータ取得のためにMackerelのAPIを叩くため、APIKEYが必要です
- HOST_ID(例: `2GyUJSydbQq`)には収集したいホストidを記述してください
- METRIC_NAME(例: `loadavg5`や`cpu.user.percentage`など)には収集したいメトリック名を記述してください
  - ワイルドカード指定は今のところできません
- `max_check_attempts`はなくてもよいですが、時々タイムアウトでUNKNOWNになってしまうため、付けておいたほうが安心です

```
[plugin.checks.anomaly_mac_pro]
command = "/usr/local/bin/docker run --rm -e MACKEREL_APIKEY=XXXXX -v /tmp:/tmp yasuhisa/mackerel_ts_anomaly_detection /app/run.sh HOST_ID METRIC_NAME"
max_check_attempts = 2
```
