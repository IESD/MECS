"""
Testing the INA3221Device
"""
import logging
import copy

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

import pytest

from MECS.data_acquisition.devices.ina3221 import INA3221Device, INA3221DataPoint, INA3221Error

# Happy tests - this is how it should work

config = {
    "data_points": {
        "daq_load_current": {
            "channel": 1,
            "type": "current"
        },
        "daq_bus_voltage": {
            "channel": 1,
            "type": "busVoltage"
        },
        "usb_load_current": {
            "channel": 2,
            "type": "current"
        },
        "load_bus_voltage": {
            "channel": 2,
            "type": "busVoltage"
        }
    }
}

def test_valid_config():
    ina = INA3221Device(hardware_required=False, **config)
    assert len(ina.data_points) == 4
    data_point = ina.data_points['daq_load_current']
    assert isinstance(data_point, INA3221DataPoint)
    assert data_point.type == "current"
    assert str(ina) == "INA3221(current_1: 'daq_load_current', busVoltage_1: 'daq_bus_voltage', current_2: 'usb_load_current', busVoltage_2: 'load_bus_voltage')"
    readings = ina.readings()
    assert 'daq_load_current' in readings


def test_invalid_type():
    c = copy.deepcopy(config)
    c['data_points']['load_bus_voltage']['type'] = "invalid value"
    with pytest.raises(INA3221Error) as e:
        ina = INA3221Device(hardware_required=False, **c)
    assert "Unknown type 'invalid value'" in str(e)

