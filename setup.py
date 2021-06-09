from setuptools import setup, find_packages

setup(
  name='MECS',
  version="0.2.1",
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'numpy',
    'pandas',
    'matplotlib',
    'smbus',
    'pyserial',
  ],
  entry_points = """
    [console_scripts]
    mecs-status = MECS.cli:status
    mecs-init = MECS.cli:init
    mecs-generate = MECS.cli:generate
    mecs-aggregate = MECS.cli:aggregate
    mecs-register = MECS.cli:register
    mecs-upload = MECS.cli:upload
    mecs-test = MECS.cli:test
    mecs-test2 = MECS.cli:test2
    mecs-plot = MECS.cli:plot
    mecs-test-connection = MECS.cli:test_connection
    """
)
