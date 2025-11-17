# rqalpha-futu-datasource

由于RQAlpha框架提供的数据，需要付费，并且只有A股的数据。
因此为RQAlpha框架提供自定义的Futu数据源，同时支持A股、港股、美股。用于基于rqalpha框架的回测。

## 用法

### 安装

- `pip install rqalpha futu-api`
- 在本项目根目录安装：`pip install -e .`

### 下载原始数据到本地

- 启动本地 OpenD（默认 `127.0.0.1:11111`）
- 运行下载脚本，将数据保存为 CSV：
  - `python -m rqalpha_futu_datasource.download --data-dir data --codes 000001.XSHE,600000.XSHG,00700.XHKG,US.AAPL --periods 1m,3m,5m,1d,1w,1mo --start 2024-01-01 --end 2024-12-31`
  - 或使用代码文件：`python -m rqalpha_futu_datasource.download --data-dir data --code-file ./codes.txt`
- 目录结构：`data/<MARKET>/<SYMBOL>/<period>.csv`，例如：`data/SZ/000001/1d.csv`
- 可通过环境变量指定目录：`set FUTU_DATA_DIR=...`（Windows）

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

- 代码格式支持 `RQAlpha`（如 `000001.XSHE`、`600000.XSHG`、`00700.XHKG`、`US.AAPL`）与 `Futu`（如 `SZ.000001`、`SH.600000`、`HK.00700`、`US.AAPL`）。
- 已实现股票回测相关方法，包括 `history_bars`、`get_bar`、`available_data_range`、`is_suspended`。
- 当前支持周期 `1d`、`1m` 的读取；更长周期可直接下载相应 CSV 或基于 `1m` 重采样后使用。
