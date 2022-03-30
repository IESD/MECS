# MECS

A python library for monitoring multiple sensor values on a MECS raspberry PI.

> This is a draft tool at the moment, subject to change

## Set up an sd-card

1. Flash raspberry pi OS (32bit lite) to an sd-card (minimum 32GB).
1. Enable headless ssh access by adding a file named `ssh` into the boot partition
```bash
cd /path/to/boot/partition
touch ssh
```
3. Insert sd card into your raspberry pi

4. Log into the pi via ssh
> HINT: If you have problems with this, try using putty to connect - this worked for us in the lab

## Initialise the pi

1. Set the pi user password
```bash
passwd
```

1. Download the installation script
```bash
wget https://raw.githubusercontent.com/IESD/MECS/master/scripts/make_mecs.sh
```

1. Make the script executable
```bash
sudo chmod 777 make_mecs.sh
```

1. Execute the script
```bash
sudo ./make_mecs.sh
```

This will install a lot of stuff.
You will see lots of output.
Check for any errors.

## Configuration

A configuration file is needed to use the system.
A template is provided.
By default, a copy of this will be placed in `~/.MECS/MECS.ini`.
For advanced usage, a configuration file can be specified as the first and only argument for all the following commands.

## Usage

To get a readout of the current status

```bash
mecs-status

> *********************************************
> * MECS version: 0.1.0                       *
> *         conf: /home/graeme/.MECS/MECS.ini *
> *      UNIT_ID: unidentified                *
> *           DT: 2021-05-22 09:34:37 (UTC)   *
> *********************************************

```

To initialise the `UNIT_ID` to a user-specified value.

```bash
mecs-init
> Enter a new Unit ID (currently not set): MECS-0001
```

To begin a long-running monitoring process which saves data files every minute.

```bash
mecs-generate
```

> mecs-generate is automatically enabled as a service (i.e. will always be running)
> To manage it, use `systemctl`
```
sudo systemctl stop mecs-generate
sudo systemctl start mecs-generate
sudo systemctl disable mecs-generate
sudo systemctl enable mecs-generate
```

To aggregate generated files into a single file for upload.

```bash
mecs-aggregate
```
> This is automatically scheduled via `cron` so probably just leave it
if you want to tweak it, edit the crontab for the pi user
```
crontab -e
```

To communicate with a server requires `username`, `host` and `port` to be set in configuration file.

> these need to be set to a user and server that will receive the data via ssh

In order to register, you also need `destination_root` and `archive_folder` to be set in the configuration file.

> the defaults are fine for this

Calling `mecs-register` will set up a public key on the server and create the necessary folders on the server and locally.

```bash
mecs-register
```
> This won't work if you don't have a server configured and ready

To upload aggregated data to the server

```bash
mecs-upload
```
> Again, this is already configured in cron

To work correctly, `mecs-upload` requires the same server parameters to be set as for `mecs-register`.
