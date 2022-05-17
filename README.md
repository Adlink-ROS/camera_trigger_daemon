# Camera Trigger Daemon

Frame Synchronization with external signal.

MTi 670/680 with GNSS ⇒  Send 1 PPS

ROScube X with mraa ⇒ GPIO ⇒ Trigger ISR + Camera
 
# Installation

## Mraa

```bash
sudo add-apt-repository ppa:mraa/mraa
sudo apt-get update
sudo apt-get install libmraa2 libmraa-dev libmraa-java 
sudo apt-get install python-mraa python3-mraa node-mraa mraa-tools
```

## Neuron Library

```bash
# Setup ADLINK APT repository
sudo apt install curl
curl -L --insecure https://neuron.adlinktech.com/debian/repo_signing.key | sudo apt-key add -
echo 'Acquire::https::neuron.adlinktech.com::Verify-Peer "false";' | sudo tee /etc/apt/apt.conf.d/99roscube > /dev/null
echo 'Acquire::https::neuron.adlinktech.com::Verify-Host "false";' | sudo tee -a /etc/apt/apt.conf.d/99roscube > /dev/null
echo "deb [arch=$(dpkg --print-architecture)] https://neuron.adlinktech.com/debian/common$(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/roscube.list > /dev/null
sudo apt update

# Install Neuron Library
sudo apt install neuron-library
```

## Get the code

```bash
git clone https://github.com/Adlink-ROS/camera_trigger_daemon.git
cd camera_trigger_daemon/
```

# Usage

## ****Frame Sync Configuration****

RQX-58G supports **Free Run Mode** and **Frame Sync Mode**.

- 0 -> Free Run mode
- 1 -> Frame Sync mode

```bash
su root
# If you want Frame Sync mode
echo 1 > /sys/module/leopard_ar0233/parameters/trigger_mode
i2cset -f -y 2 0x66 0x04 0xff
# If you want Free Run mode
echo 0 > /sys/module/leopard_ar0233/parameters/trigger_mode
i2cset -f -y 2 0x66 0x04 0xf0

# check the Frame mode
cat /sys/module/leopard_ar0233/parameters/trigger_mode
```

## Camera Daemon

We provide a daemon to trigger cameras when GPIO interrupts by external signal.

The daemon provides four function:

* Start : trigger cameras with external signal.
* Stop : stop the daemon.
* Restart : stop and then start.
* Start_free : trigger cameras without external signal.

### To start the daemon

```bash
sudo python3 isr_camera.py start
```

### To stop the daemon

```bash
sudo python3 isr_camera.py stop
```

### To restart the daemon

```bash
sudo python3 isr_camera.py restart
```

### To start the daemon without the PPS

```bash
sudo python3 isr_camera.py start_free
```

## Warning

If the daemon didn't work, please check the ``daemon.log`` file.