# Copyright 2026 weewx-packages
# Distributed under the terms of the GNU Public License (GPLv3)
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest
import usb
import weecfg
import weewx

spec = importlib.util.spec_from_file_location('wh23xx', Path(__file__).parents[1] / 'bin/user/wh23xx.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_history_python3_integer_fields():
    packet = m.WH23xxStation.decode_history_record([0] * 18)
    assert packet['wind_speed'] == 0
    assert packet['rain_total'] == 0


def test_checksum_split_at_exact_record_length():
    station = m.WH23xxStation()
    station._write = Mock()
    station.devh = Mock()
    payload = [1, 2, 3, 4]
    checksum = m._calc_checksum([station.READ_RECORD, len(payload)] + payload)
    station.devh.interruptRead.side_effect = [
        [1, 8, station.READ_RECORD, 4] + payload,
        [1, 3, checksum],
    ]
    assert station._read_record() == payload
    assert station.devh.interruptRead.call_count == 2


def test_invalid_checksum_rejected():
    station = m.WH23xxStation()
    station._write = Mock()
    station.devh = Mock()
    station.devh.interruptRead.return_value = [1, 8, station.READ_RECORD, 2, 1, 2, 255]
    with pytest.raises(weewx.WeeWxIOError, match='checksum mismatch'):
        station._read_record()


def test_usb_timeout_is_bounded(monkeypatch):
    monkeypatch.setattr(m.time, 'sleep', lambda _: None)
    driver = object.__new__(m.WH23xxDriver)
    driver.max_tries = 2
    driver.retry_wait = 0
    driver._station = Mock()
    driver._station.get_current.side_effect = [usb.USBError('No data available')] * 2 + [RuntimeError('unbounded retry')]
    with pytest.raises(weewx.RetriesExceeded):
        driver._get_current()
    assert driver._station.get_current.call_count == 2


def test_usb_ids():
    station = m.WH23xxStation('0x1234', '0xabcd')
    assert (station.vendor_id, station.product_id) == (0x1234, 0xabcd)


def test_configurator_opens_one_handle(monkeypatch, capsys):
    station = Mock()
    station.__enter__ = Mock(return_value=station)
    station.__exit__ = Mock(return_value=False)
    station.get_station_info.return_value = {'model': 'WH2310', 'debug': 'hidden'}
    cls = Mock(return_value=station)
    monkeypatch.setattr(m, 'WH23xxStation', cls)
    configurator = m.configurator_loader({})
    parser = configurator.get_parser()
    configurator.add_options(parser)
    options, _ = parser.parse_args(['--info'])
    configurator.do_options(options, parser, {m.DRIVER_NAME: {}}, True)
    cls.assert_called_once()
    station.get_station_info.assert_called_once()
    assert capsys.readouterr().out == 'model: WH2310\n'


def test_confeditor_import_with_weewx(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / 'bin'))
    editor, name, version = weecfg.load_driver_editor('user.wh23xx')
    assert name == 'WH23xx'
    assert 'user.wh23xx' in editor.default_stanza
    assert version == '0.15.1'


def test_standalone_test_decode_info():
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[1] / 'bin'))
    result = subprocess.run([sys.executable, '-m', 'user.wh23xx', '--action=test-decode-info'],
                            env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "'model': '0x0023'" in result.stdout
