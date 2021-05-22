# MECS

A python library for monitoring multiple sensor values on a MECS raspberry PI.

> This is a draft tool at the moment, subject to change

## Installation

Installing is via the `setup.py` file for now.

```bash
python setup.py install
```

A configuration file is needed to use the system.
A template is provided.
By default, a copy of this should be placed in `~/.MECS/MECS.ini`.
For advanced usage, a configuration file can be specified as the first and only argument for the following commands.

## Usage

To get a readout of the current status

```bash
mecs-status

> *********************************************
> * MECS version: 0.1.0                       *
> *         conf: /home/graeme/.MECS/MECS.ini *
> *  HARDWARE_ID: unidentified                *
> *      UNIT_ID: unidentified                *
> *           DT: 2021-05-22 09:34:37 (UTC)   *
> *********************************************

```

To initialise a pi with a unique `HARDWARE_ID` and to set the `UNIT_ID` to a user-specified integer.

```bash
mecs-init
> Enter a new Unit ID (currently not set): 1
```

To begin a long-running monitoring process which saves data files every minute.

```bash
mecs-generate
```

To aggregate generated files into a single file for upload.
This is expected to be scheduled via `cron`.

```bash
mecs-aggregate
```
