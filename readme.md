# MECS

A python library for monitoring multiple sensor values on a MECS raspberry PI.

> This is a draft tool at the moment, subject to change

## Set up an sd-card

1. Flash raspberry pi OS (32bit lite) to an sd-card (minimum 32GB).
1. Enable headless ssh access by adding a file named `ssh` into the boot partition

   To do this when flashing card from Windows:

    1. Open My Computer in Windows Explorer
    1. Navigate to SD card boot partition (will show as a drive)
    1. Right click, create new text file, rename as ssh with no file suffix

    from Linux: 
    ```bash
    cd /path/to/boot/partition
    touch ssh
    ```
1. Insert sd card into your raspberry pi

1. Log into the pi via ssh with default password: `raspberry`
> HINT: If you have problems with this, try using putty to connect - this worked for us in the lab

## Initialise the pi

1. Set the pi user password
```bash
passwd
```

1. Download the installation script
```bash
wget https://raw.githubusercontent.com/IESD/MECS/master/scripts/make_mecs.sh -O make_mecs.sh
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

A nice way to check for errors is to append the following to the above command, which sends output to a log file that you can search as well as echoing to the terminal

```bash
|& tee -a log.txt
```

## Configuration

A configuration file is needed to use the system.
A template is provided.
By default, a copy of this will be placed in `~/.MECS/MECS.ini`.
For advanced usage, a configuration file can be specified as the first and only argument for all the following commands.

## Usage

### mecs-status

To get a readout of the current status

```bash
mecs-status

>***************************************************
>* MECS version: 0.3.0                             *
>***************************************************
>*         conf: /home/pi/MECS/MECS.ini            *
>*      UNIT_ID: unidentified                      *
>*           DT: 2022-10-24 13:35:40 (UTC)         *
>*       Server: username@host.com:22              *
>***************************************************

```

> You may get an error message regarding the server configuration
> In which case, you should run mecs-init

### mecs-init

This is essential to initialise the unit identifier, type and server configuration.

```bash
mecs-init
> Enter a new Unit ID (currently not set): MECS-0001
> Unit type (AC or DC, currently AC): AC
> Host (currently not set): my.server.com
> Username (currently not set): mecs_0001
```

### mecs-register

Calling `mecs-register` will set up a public key on the server and create the necessary folders on the server and locally.

To communicate with a server requires the `username` and `host` settings to be configured using the `mecs-init` script.

```bash
mecs-register
```
> You will be asked to authenticate on the server.
> This won't work if you don't have a server configured and ready.


>In order to register, you also need `destination_root` and `archive_folder` to be set in the configuration file.
> the default values are fine for this


### mecs-generate

To begin a long-running monitoring process which saves data files every minute.

```bash
mecs-generate
```

> mecs-generate is automatically enabled as a service (i.e. will always be running)
> To manage it, use `systemctl`
>```
>sudo systemctl stop mecs-generate
>sudo systemctl start mecs-generate
>sudo systemctl disable mecs-generate
>sudo systemctl enable mecs-generate
>```

### mecs-aggregate

To aggregate generated files into a single file for upload.

```bash
mecs-aggregate
```
> This is automatically scheduled via `cron` so probably just leave it
if you want to tweak it, edit the crontab for the pi user
```
crontab -e
```

### mecs-upload

To upload aggregated data to the server

```bash
mecs-upload
```
> Again, this is already configured in cron

To work correctly, `mecs-upload` requires the same server parameters to be set as for `mecs-register`.
