from setuptools import setup, find_packages

setup(
  name='MECS',
  version="0.3.0",
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'numpy',
    'pandas',
    'smbus',
    'pyserial',
    'w1thermsensor',
  ],
  entry_points = """
    [console_scripts]
    mecs-test = MECS.cli:test
    mecs-test2 = MECS.cli:test2
    mecs-status = MECS.cli:status
    mecs-init = MECS.cli:initialise
    mecs-generate = MECS.cli:generate
    mecs-aggregate = MECS.cli:aggregate
    mecs-register = MECS.cli:register
    mecs-upload = MECS.cli:upload
    mecs-test-connection = MECS.cli:test_connection
    mecs-update = MECS.cli:update
    mecs-calibrate = MECS.cli:calibrate
    """
)
