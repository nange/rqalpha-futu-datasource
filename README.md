# rqalpha-futu-datasource

由于RQAlpha股票回测框架提供的数据，需要付费(还挺贵)，并且只有A股的数据。
因此为RQAlpha框架提供自定义的Futu(富途)数据源，同时支持A股、港股、美股数据。用于基于rqalpha框架的股票回测。

## 用法

### 安装

- `pip install rqalpha futu-api`
- 在本项目根目录安装：`pip install -e .`

### 下载富途原始数据到本地

- 启动本地 OpenD（默认 `127.0.0.1:11111`）
- 运行下载脚本，将数据保存为 CSV：
  - `python -m rqalpha_futu_datasource.download --data-dir data --codes 000001.XSHE,600000.XSHG,00700.XHKG,US.AAPL --periods 1m,3m,5m,1d,1w,1mo --start 2024-01-01 --end 2024-12-31`
  - 或使用代码文件：`python -m rqalpha_futu_datasource.download --data-dir data --code-file ./codes.txt`
- 目录结构：`data/<MARKET>/<SYMBOL>/<period>.csv`，例如：`data/SZ/000001/1d.csv`
- 可通过环境变量指定目录：`set FUTU_DATA_DIR=...`（Windows）

> 注意：
>
> - 下载富途原始数据时，也可以指定富途OpenD的地址和端口号，如"--host 192.168.0.2 --port 22222"
> - 为了使用方便，`--codes`的格式同时支持富途的股票代码格式（如 `SZ.000001`、`SH.600000`、`HK.00700`、`US.AAPL`）与 `RQAlpha` 的股票代码格式（如 `000001.XSHE`、`600000.XSHG`、`00700.XHKG`、`AAPL.XNAS`）。
> - 同时，`--code-file`参数也支持同时包含这两种格式的股票代码，每个股票代码占一行。
> - 但回测代码里面的股票代码格式，必须是 `RQAlpha` 格式（如 `000001.XSHE`、`600000.XSHG`、`00700.XHKG`、`AAPL.XNAS`）。

### 在 RQAlpha 中启用 Futu 数据源

通过扩展模块替换默认 DataSource：

1. 新建扩展文件 `rqalpha_futu_ext.py`：

   ```python
   import os
   from rqalpha_futu_datasource import FutuDataSource

   def load_ext(context):
       data_dir = os.getenv("FUTU_DATA_DIR", os.path.join(os.getcwd(), "data"))
       ds = FutuDataSource(data_dir=data_dir)
       context.env.set_data_source(ds)
   ```

2. 运行回测（示例）：
   - `rqalpha run -f strategy.py -s 2024-11-01 -e 2024-11-30 --account stock 100000 --extend rqalpha_futu_ext.py`

说明：

- 已实现股票回测相关方法，包括 `history_bars`、`get_bar`、`available_data_range`、`is_suspended`。
- 当前支持周期 `1d`、`1m` 的读取；更长周期可直接下载相应 CSV 或基于 `1m` 重采样后使用。
- RQAlpha与富途股票代码之间的对应关系是：
  - A股：`000001.XSHE` -> `SZ.000001` (深圳交易所)
  - A股：`603728.XSHG` -> `SH.603728` (上海交易所)
  - 港股：`00700.XHKG` -> `HK.00700`  (香港交易所)
  - 美股：`AAPL.XNAS` -> `US.AAPL`  (纳斯达克交易所)
  - 美股：`TSM.XNYS` -> `US.TSM`  (纽约交易所)
