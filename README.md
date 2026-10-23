# Fine Offset WH23xx for WeeWX

A WeeWX driver that collects current observations from a Fine Offset WH23xx
console over USB: temperature, humidity, wind and gust, pressure, rain, light
and UV. The source names the WH2300, WH2301, WH4000 and Tycon TP2700. Matching a
brand or USB ID alone does not establish protocol compatibility.

This is an independent continuation of
[matthewwall/weewx-wh23xx](https://github.com/matthewwall/weewx-wh23xx), ported
to Python 3 with checksum checks across USB packets and a `weectl device`
configurator. [NOTICE](NOTICE) credits the upstream work it builds on.

## Requirements

- A WH23xx console connected over USB.
- The platform USB backend. Debian and Ubuntu provide it in `libusb-1.0-0`.
- Access to the USB device for the user that runs WeeWX.
- The Python USB library, installed in the Python environment that runs WeeWX:

  ```sh
  python -m pip install 'pyusb>=1,<2'
  ```

  Activate that environment first, so that `python` and `weectl` both come from
  it. For an OS-packaged WeeWX, install the distribution package for PyUSB
  instead.

## Installation

Install `wh23xx` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/wh23xx.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

Then select the driver and restart WeeWX:

```sh
weectl station reconfigure --driver=user.wh23xx --config=/path/to/weewx.conf
```

## Configuration

```ini
[Station]
    station_type = WH23xx

[WH23xx]
    driver = user.wh23xx
```

| Option | Default | Meaning |
|---|---|---|
| `model` | `Tycon TP2700` | Hardware name that WeeWX reports. |
| `poll_interval` | `15` | Seconds between reads of current data. |
| `max_tries` | `5` | Read attempts before the driver gives up. |
| `retry_wait` | `10` | Seconds between read attempts. |
| `vendor_id` | `0x10c4` | USB vendor ID of the console. |
| `product_id` | `0x8468` | USB product ID of the console. |
| `debug_rain` | `0` | Set to `1` to log each change of the rain counter. |

Change the USB IDs only for a device known to use the WH23xx protocol.

The driver reports in `METRICWX` units. `UV` holds the UV index from the
console. `radiation` is computed from `luminosity` with a fixed factor of
0.0079. The raw UV reading goes into `uv_raw`, which the default WeeWX schema
does not store.

### Device diagnostics

Only one process can use the console. Stop WeeWX before you run these, and
restart it afterwards:

```sh
weectl device --help --config=/path/to/weewx.conf
weectl device --info --config=/path/to/weewx.conf
weectl device --current --config=/path/to/weewx.conf
```

The configurator also provides `--info-all`, `--eeprom-time`,
`--eeprom-dump-raw`, `--sync-time` and `--clear-history`. The last two change
the console and ask for confirmation unless you pass `-y`. Do not clear the
history to diagnose a read failure.

For read failures, check the WeeWX log for USB permission errors, checksum
mismatches and exceeded retries.

## Limitations

- Not tested on WH23xx hardware by weewx-packages.
- The driver reads current data only. It does not import the history stored in
  the console.
- `radiation` is an approximation derived from light, not a measurement.
- The tests decode recorded byte sequences. They cannot show that a console
  receives its outdoor sensors.

## Development

Run the tests in a Python environment with WeeWX, PyUSB and pytest:

```sh
python -m pytest -q tests
```

## License

Copyright 2016 Matthew Wall. Distributed under the GNU General Public License
version 3; see [license](license). The source carries the protocol notes and
credits Lloyd Kinsella.
