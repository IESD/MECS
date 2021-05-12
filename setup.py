from setuptools import setup, find_packages

setup(
  name='MECS',
  version="0.0.3",
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'numpy',
    'pandas'
  ],
  entry_points = """
    [console_scripts]
    mecs-init = MECS.initialisation:main
    mecs-generate = MECS.data_management:generate
    mecs-aggregate = MECS.data_management:aggregate
    """
)
