"""
Testing the ADCDevice and ADCSensor
"""
import pytest

from MECS.data_acquisition.devices.adc import ADCDevice, ADCSensor, ADCError

# Happy tests - this is how it should work

def test_with_empty_sensors():
    adc = ADCDevice(hardware_required=False, **{
        "input_impedance": 1000.5,
        "bit_rate": 1,
        "sensors": {}
    })
    assert isinstance(adc, ADCDevice)
    assert adc.readings() == {}

def test_with_valid_voltage_channel():
    config = {
        "device": "ADCPi",
        "input_impedance": 10,
        "bit_rate": 12,
        "sensors": {
            "your label": {
                "type": "voltage",
                "channel": 1,
                "zero_point": 0,
                "resistance": 50.5
            }
        }
    }
    adc = ADCDevice(hardware_required=False, **config)
    assert len(adc.sensors) == 1
    sensor = adc.sensors['your label']
    assert isinstance(sensor, ADCSensor)
    assert sensor.type == "voltage"
    assert sensor.sensitivity == 6.05
    assert str(adc) == "ADC(ch_1: 'your label')"
    assert vars(sensor) == {
        "type": "voltage",
        "channel": 1,
        "zero_point": 0.0,
        "ref_channel": None,
        "resistance": 50.5,
        "sensitivity": 6.05
    }
    assert sensor.config() == {
        "type": "voltage",
        "channel": 1,
        "zero_point": 0.0,
        "ref_channel": None,
        "resistance": 50.5,
    }
    assert adc.config() == {
        "device": "ADCPi",
        "address1": 104,
        "address2": 105,
        "input_impedance": 10.0,
        "bit_rate": 12,
        "sensors": {
            "your label": {
                "type": "voltage",
                "channel": 1,
                "ref_channel": None,
                "zero_point": 0,
                "resistance": 50.5
            }
        }
    }


def test_with_valid_current_channel():
    adc = ADCDevice(hardware_required=False, **{
        "input_impedance": 10,
        "bit_rate": 12,
        "sensors": {
            "your label": {
                "type": "current",
                "channel": 1,
                "zero_point": 0,
                "milliVoltPerAmp": 10000
            }
        }
    })
    assert len(adc.sensors) == 1
    sensor = adc.sensors['your label']
    assert isinstance(sensor, ADCSensor)
    assert sensor.type == "current"
    assert sensor.sensitivity == 0.1
    assert str(adc) == "ADC(ch_1: 'your label')"


# Unhappy tests for helpful error messages
# If you get a rubbish error message, decide what should happen and create a failing test here


def test_without_config():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(**{})
    assert "Missing parameter: 'input_impedance'" in str(e)

def test_with_missing_bit_rate():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(**{
            "input_impedance": "test"
        })
    assert "Missing parameter: 'bit_rate'" in str(e)

def test_with_missing_sensors():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(**{
            "input_impedance": "test",
            "bit_rate": "lots"
        })
    assert "Missing parameter: 'sensors'" in str(e)

def test_with_invalid_impedance():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(**{
            "input_impedance": "test",
            "bit_rate": "lots",
            "sensors": {}
        })
    assert "input_impedance: 'test' must be a number" in str(e)

def test_with_invalid_bit_rate():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(**{
            "input_impedance": 1000,
            "bit_rate": "lots",
            "sensors": {}
        })
    assert "bit_rate: 'lots' must be an integer" in str(e)

def test_with_invalid_sensors():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(**{
            "input_impedance": 1000,
            "bit_rate": 16,
            "sensors": "this is invalid"
        })
    assert "'sensors' must be a dictionary" in str(e)

def test_with_missing_channel():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(hardware_required=False, **{
            "input_impedance": 1.5,
            "bit_rate": 200000,
            "sensors": {
                "your label": {}
            }
        })
    assert "channel ['your label']: missing required field 'channel'" in str(e)

def test_with_missing_type():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(hardware_required=False, **{
            "input_impedance": 1.5,
            "bit_rate": 12,
            "sensors": {
                "your label": {
                    "channel": 1
                }
            }
        })
    assert "channel ['your label']: missing required field 'type'" in str(e)

def test_with_missing_zero_point():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(hardware_required=False, **{
            "input_impedance": 1.5,
            "bit_rate": 1.5,
            "sensors": {
                "your label": {
                    "channel": 1,
                    "type": "voltage",
                }
            }
        })
    assert "channel ['your label']: missing required field 'zero_point'" in str(e)

def test_with_invalid_channel():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(hardware_required=False, **{
            "input_impedance": 1.5,
            "bit_rate": 12,
            "sensors": {
                "your label": {
                    "type": "voltage",
                    "channel": "needs an integer",
                    "zero_point": 0
                }
            }
        })
    assert "channel ['your label']: channel: 'needs an integer' (expected integer)" in str(e)

def test_with_invalid_zero_point():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(hardware_required=False, **{
            "input_impedance": 1.5,
            "bit_rate": 12,
            "sensors": {
                "your label": {
                    "type": "voltage",
                    "channel": 1,
                    "zero_point": "needs a float"
                }
            }
        })
    assert "channel ['your label']: zero_point: 'needs a float' (expected float)" in str(e)

def test_with_invalid_voltage_channel():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(hardware_required=False, **{
            "input_impedance": 1.5,
            "bit_rate": 12,
            "sensors": {
                "your label": {
                    "type": "voltage",
                    "channel": 1,
                    "zero_point": 0
                }
            }
        })
    assert "channel ['your label']: voltage sensors require 'resistance' field to be set" in str(e)


def test_with_invalid_current_channel():
    with pytest.raises(ADCError) as e:
        adc = ADCDevice(hardware_required=False, **{
            "input_impedance": 1.5,
            "bit_rate": 12,
            "sensors": {
                "your label": {
                    "type": "current",
                    "channel": 1,
                    "zero_point": 0
                }
            }
        })
    assert "channel ['your label']: current sensors require 'milliVoltPerAmp' field to be set" in str(e)

