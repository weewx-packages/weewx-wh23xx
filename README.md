# Fine Offset WH23xx for WeeWX

Collect weather observations from a Fine Offset WH23xx console over USB. The
upstream hardware notes include Tycon TP2700 and Froggit WH4000 variants. The
driver supplies temperature/humidity, wind/gust, pressure, light, UV and rain.
Matching a brand or USB ID alone does not establish protocol compatibility.

This independent continuation preserves
[matthewwall/weewx-wh23xx](https://github.com/matthewwall/weewx-wh23xx) history.
Release 0.15.0 includes Python 3 decoding, checksum/retry handling and WeeWX's
device configurator. No WH2303/WH2310/WH2315 hardware check is claimed here.

## Install

The catalog release requires Python >=3.10 and WeeWX >=5.2,<6.

Install `pyusb` in the WeeWX Python environment and the platform USB backend,
such as libusb. Grant the WeeWX service user access to the console:

```sh
python -m pip install pyusb
```

Use the `weectl` from your WeeWX Python environment:

```sh
weectl extension install https://github.com/weewx-packages/weewx-wh23xx/releases/download/v0.15.0/weewx-wh23xx-0.15.0.zip --config=/path/to/weewx.conf
weectl station reconfigure --driver=user.wh23xx --config=/path/to/weewx.conf
```

Replace `/path/to/weewx.conf` with your station configuration. Stock WeeWX 5
accepts this fixed URL or a downloaded copy of the same archive. No catalog
integration is required. Restart WeeWX yourself after configuration changes.

## Select USB acquisition

```ini
[Station]
    station_type = WH23xx
[WH23xx]
    driver = user.wh23xx
    poll_interval = 15
    vendor_id = 0x10c4
    product_id = 0x8468
```

Change USB IDs only for a device known to use the WH23xx protocol. Only one
process should access the console. Stop WeeWX before using device diagnostics:

```sh
weectl device --help --config=/path/to/weewx.conf
weectl device --info --config=/path/to/weewx.conf
weectl device --current --config=/path/to/weewx.conf
```

The configurator also provides `--info-all`, `--eeprom-time`,
`--eeprom-dump-raw`, `--sync-time` and `--clear-history`. The last two change the
device and prompt first. Do not clear history to diagnose a read failure.
Restart WeeWX after standalone access. Check logs for USB permissions, failed
checksums or exhausted retries; offline decoding cannot establish RF reception.

Copyright 2016 Matthew Wall. GPL-3.0-only; see [license](license).
[NOTICE](NOTICE) credits ra1u's Python 3 proposal and the original device
configuration interface. Source protocol notes remain in
[wh23xx.py](bin/user/wh23xx.py).

<!-- Documentation updated 2026-10-23 by weewx-packages. -->
