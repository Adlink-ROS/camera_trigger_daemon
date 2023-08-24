# Camera Trigger Daemon

Frame Synchronization with external signal.

MTi 670/680 with GNSS ⇒  Send 1 PPS

ROScube X with mraa ⇒ GPIO ⇒ Trigger ISR + Camera
 
# Installation

## Neuron Library

Download Neuron Library from the link: https://github.com/Adlink-ROS/mraa/releases

And then install Neuron Library from the deb file:
```bash
# Example for RQX-58G
sudo apt install neuron-library_1.3.13_arm64_ubuntu1804.deb
```

## Get the code

```bash
git clone https://github.com/Adlink-ROS/camera_trigger_daemon.git
cd camera_trigger_daemon/
```

# Usage

## ****Camera Sync Configuration****

RQX-58G supports **Free Run Mode** and **Frame Sync Mode**.

- 0 -> Free Run mode
- 1 -> Frame Sync mode

For more details, you can go to [Frame Synchronization](https://adlink-ros.github.io/roscube-doc/roscube-x/gmsl_camera/frame_sync.html).

## Camera Daemon

We provide a daemon to trigger cameras when GPIO interrupts by external signal.

```bash
sudo python3 adlink_camera_sync [mode] [-f freq] [-t gpio_num] [-h help]
```
* mode:
    - sync:
         1. set frame sync mode
         2. enable isr if gpio_num != None
         3. enable trigger daemon
    - free:
         1. disable trigger daemon
         2. set free run mode
* While sync mode, supports two options
    - freq: the trigger frequency (default 5 Hz) range from 1 to 20 Hz
    - gpio_num: whether triggered by GPIO in
    - help: more detail about argument

### Sync mode

```bash
# Trigger camera directly by 5 Hz(default) without ISR.
sudo python3 adlink_camera_sync sync
# Oprional: trigger camera by 10 Hz with ISR (from GPIO_NUM 5).
sudo python3 adlink_camera_sync sync -f 10 -t 5
```

### Free mode

```bash
sudo python3 adlink_camera_sync free 
```

## Warning

When run **Sync mode**, show the message "pidfile /tmp/daemon-example.pid already exist. Daemon already running?".

That means ``pid`` of daemon already exist, you need stop the daemon by running **Free mode** first.

If the daemon didn't work, please check the ``daemon.log`` file.
