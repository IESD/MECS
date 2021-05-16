from setuptools import setup, find_packages

setup(
  name='MECS',
  version="0.0.5",
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'numpy',
    'pandas'
  ],
  entry_points = """
    [console_scripts]
    mecs-status = MECS.data_management:status
    mecs-init = MECS.data_management:initialise
    mecs-generate = MECS.data_management:generate
    mecs-aggregate = MECS.data_management:aggregate
    mecs-register = MECS.communication:initialise
    mecs-upload = MECS.communication:upload
    """
)
