# rqalpha-futu-datasource

由于RQAlpha股票回测框架提供的数据，需要付费(还挺贵)，并且只有A股的数据。
因此为RQAlpha框架提供自定义的Futu(富途)数据源，同时支持A股、港股、美股数据。用于基于rqalpha框架的股票回测。

## 用法

### 本地开发

推荐使用`uv`工具管理项目依赖。执行以下命令安装项目依赖：

```bash
make sync
```

后续即可做开发和测试。

### 安装

- `pip install rqalpha-futu-datasource`

### 下载富途原始数据到本地

- 启动本地 OpenD(默认 `127.0.0.1:11111`)
- 运行下载脚本，将数据保存为 CSV：
  - `python -m rqalpha_futu_datasource.download --data-dir data --codes 000001.XSHE,600000.XSHG,00700.XHKG,US.AAPL --periods 1m,3m,5m,1d,1w --start 2024-01-01 --end 2024-12-31`
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

通过扩展模块替换默认DataSource。参考：[test_rqalpha_example.py](tests/test_rqalpha.py), [mod_futu_ds.py](src/rqalpha_futu_datasource/mod_futu_ds.py)

关键代码：

```python
def test_run_with_futu_datasource():
    config = {
        "base": {
            "start_date": "2024-11-01",
            "end_date": "2024-11-06",
            "accounts": {"stock": 100000},
            "frequency": "1m",
            "data_bundle_path": os.path.abspath("tests/data"),
        },
        "extra": {
            "log_level": "info",
        },
        "mod": {
            "futu_ds": {
                "enabled": True,
                "lib": "rqalpha_futu_datasource.mod_futu_ds",
            },
            "sys_analyser": {},
        },
    }
    run_func(init=init, handle_bar=handle_bar, config=config)
```

### 指定富途数据存储目录有三种方式

1. 在RQAlpha的模块配置中指定：

   ```python
   config = {
      "mod": {
            "futu_ds": {
                "enabled": True,
                "lib": "rqalpha_futu_datasource.mod_futu_ds",
                "futu_data_dir": "path/to/futu/data",
            },
            "sys_analyser": {},
        },
   }
   ```

2. 在RQAlpha base配置中指定：

   ```python
   config = {
       "base": {
           "data_bundle_path": "path/to/futu/data",
       },
   }
   ```

3. 在环境变量中指定：

   ```bash
   export FUTU_DATA_DIR=path/to/futu/data
   ```

优先级按此顺序：模块配置 > base配置 > 环境变量。

### 限制及说明

- 已实现关键股票回测相关方法，包括 `get_instruments`, `history_bars`、`get_bar`、`get_trading_calendar`, `available_data_range`、`is_suspended`。
- RQAlpha与富途股票代码之间的对应关系是：
  - A股：`000001.XSHE` -> `SZ.000001` (深圳交易所)
  - A股：`603728.XSHG` -> `SH.603728` (上海交易所)
  - 港股：`00700.XHKG` -> `HK.00700`  (香港交易所)
  - 美股：`AAPL.XNAS` -> `US.AAPL`  (纳斯达克交易所)
  - 美股：`TSM.XNYS` -> `US.TSM`  (纽约交易所)
- 限制：
  - 仅支持股票数据，不支持期货、期权等。
  - 原始从富途下载的数据就只能是股票前复权数据。不支持其他复权方式。
  - 数据不能增量更新，有新数据需求只能重新下载全量数据(富途的OpenD进程会本地缓存数据，所以不用太担心此问题)。
  - 回测频率支持周期 `1d`、`1m`(RQAlpha框架限制)，在handle_bar回调函数中，可以查询的历史数据周期为:`1m`, `3m`, `5m`, `1d`, `1w`(RQAlpha框架限制，无法支持到月级别)。
