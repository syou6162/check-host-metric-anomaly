# check-host-metric-anomaly
Mackerelのホストメトリックの異常検知を行なうチェック監視プラグインです。

# 概要
- 異常検知の代表的なアルゴリズムの一つであるLOF(Local Outlier Factor)を利用しています
  - 大雑把には「自分の近傍にデータ点が少ないデータほど異常である」というk近傍法的な考え方のアルゴリズムです
- ホストメトリックの時系列的な異常検知を行なえます
  - 1次元の時系列データをwindow幅(D)で区切ってD次元ベクトルに変換後、LOFに投げます
  - 取得しているAPIのエンドポイントを変えれば簡単にサービスメトリックに対しても動かせるようになるはず
- モニタリング専用のホストで動かすのがオススメです
  - アルゴリズムの学習と異常検知をagentを動かしているホスト内で行なうので、多少負荷がかかります

# Install/Build
scikit-learnを利用していますが、環境を手元で作ってもらう手間を省くためにdockerを経由して動かします。

手元で動かせるDockerイメージをDocker Hubでホストしています。Dockerが手元で動く環境であれば、以下のコマンドで使えるようになります。

```
% docker pull yasuhisa/check-host-metric-anomaly
```

修正を加えて手元でbuildすることもできます。

```
% docker build -t yasuhisa/check-host-metric-anomaly .
```

# mackerel-agent.confの書き方例
- 学習データや異常検知をする直近のデータ取得のためにMackerelのAPIを叩くため、APIKEYが必要です
- HOST_ID(例: `2GyUJSydbQq`)には収集したいホストidを記述してください
- METRIC_NAME(例: `loadavg5`や`cpu.user.percentage`など)には収集したいメトリック名を記述してください
  - ワイルドカード指定は今のところできません
- `max_check_attempts`はなくてもよいですが、時々タイムアウトでUNKNOWNになってしまうため、付けておいたほうが安心です

```conf
[plugin.checks.anomaly_sample]
command = "/usr/local/bin/docker run --rm -e MACKEREL_APIKEY=XXXXX -v /tmp:/tmp yasuhisa/check-host-metric-anomaly /app/run.sh --host-id HOST_ID --metric-name METRIC_NAME"
max_check_attempts = 2
```
