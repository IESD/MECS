import logging
import json

import pytest

from MECS import MECSConfigError
from MECS.data_acquisition.board import MECSBoard
from MECS.data_acquisition.devices.adc import ADCDevice
from MECS.data_acquisition.devices.ina3221 import INA3221Device

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def test_blank_calibration_works():
    board = MECSBoard(**{})
    assert board.devices == {}

def test_bad_section_raises():
    with pytest.raises(MECSConfigError) as e:
        board = MECSBoard(**{"your label": "config"})
    assert "section [your label] must contain a dictionary" in str(e)

def test_empty_section_raises():
    with pytest.raises(MECSConfigError) as e:
        board = MECSBoard(**{"your label": {}})
    assert "section [your label] must specify a 'device'" in str(e)

def test_unknown_device_raises():
    with pytest.raises(MECSConfigError) as e:
        board = MECSBoard(**{"your label": {
            "device": "printer"
        }})
    assert "section [your label] includes unsupported device 'printer'" in str(e)

def test_invalid_adc():
    with pytest.raises(MECSConfigError) as e:
        board = MECSBoard(**{"your label": {
            "device": "ADCPi",
        }})
    assert "[your label]" in str(e)
    assert "Missing parameter" in str(e)

def test_valid_empty_adc():
    board = MECSBoard(hardware_required=False, **{
        "test": {
            "device": "ADCPi",
            "bit_rate": 16,
            "input_impedance": 16800,
            "sensors": {}
        }
    })
    assert "test" in board.devices
    assert isinstance(board.devices['test'], ADCDevice)
    assert board.devices['test'].sensors == {}
    assert str(board) == "MECSBoard(test)"


def test_dc_config():
    with open("devices/dc.json") as f:
        dc_config = json.load(f)
    board = MECSBoard(hardware_required=False, **dc_config)
    assert "ADC" in board.devices
    assert "INA3221" in board.devices
    assert isinstance(board.devices['ADC'], ADCDevice)
    assert isinstance(board.devices['INA3221'], INA3221Device)
    readings = board.readings()
    assert isinstance(readings, dict)
    log.debug(readings)
