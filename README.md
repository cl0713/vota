# VOTA: Parallelizing 6G-RAN Experimentation with Virtualized Over-The-Air Workloads

<img width="3584" height="1205" alt="lab" src="https://github.com/user-attachments/assets/99da5637-3612-44f5-9950-ada2c41e3a94" />



![Demo video](https://tuenl-my.sharepoint.com/:v:/g/personal/c_liu3_tue_nl/EW-fgdexIuhCpHPuLGXcXJgBLwRvJQMsI4Pll5rXXj7MwA?e=xryyFv)

## Overview 
This repository contains instructions and files for setting up a virtualized 5G/6G testbed from our [paper](assets/OpenRIT6G_2025_VOTA.pdf). (Not completed yet)

## Our setup
- Workstation for gNB and core network
    - CPU: Intel Core i9-14900K
    - OS:  Ubuntu 24.04 LTS (64-bit)
    - RAM: 128 GB DDR5 RAM
    - GPU: NVIDIA RTX 4090 
- Desktop for UE
    - CPU: Intel Core i7-8700 
    - OS: Ubuntu 22.04.5 LTS
    - RAM: 16 GB DDR4 RAM
- RU: USRP X310 
- UE: Quectel 520/530

## Install LXD in both machines
Please refer to the offical documentaion: [link](https://canonical.com/lxd/install)

Install LXD as a snap
```
snap install lxd
```

Configure LXD
```
lxd init
```

Set up the web UI, for details: [link](https://documentation.ubuntu.com/lxd/stable-5.21/tutorial/ui/)
```
lxc config set core.https_address :8443
```


# Set up workstation
## 1. Create a container
```
lxc launch <image_server>:<image_name> <instance_name>
```
## 2. USRP X310 passthrough
### 2.1 Create a  `Physical Nework` for the network interface connecting to the USRP
```
lxc network create <network> --type=physical parent=<interface>
```
### 2.2 Attach USRP to the container
```
lxc network attach [<remote>:]<network> <instance> [<device name>] [<interface name>] [flags]
```
### 2.3 Set up USRP in the container 
```
sudo ifconfig <network> 192.168.40.1
sudo ethtool -G <network> tx 4096 rx 4096
sudo ip link set dev <network> mtu 9000
```

### 2.4 Install openairinterface with UHD, please refer to the offical [documentation](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/NR_SA_Tutorial_COTS_UE.md)

### 2.5 Verify if USRP is connected, there should be no errors
```
sudo uhd_usrp_probe
```

## 3 Quectel modem passthrough
### 3.1 Attach /dev/cdc-wdmX, wwanX, USB device according to `productid` and `vendorid` as `unix-hotplug`

### 3.2 Get Quectel-CM from your vendor and compile it
### 3.3 Config the modem using `minicom`






## 4. Run the experiment
### 4.1 Run gNB, list of config files we use [b78 40mhz](config/b78_40mhz.conf) [n77 100mhz](config/n77_100mhz.conf) 
```
sudo taskset -c <range of cores> nice -n -20 <path to oai>/cmake_targets/ran_build/build/nr-softmodem -O <path to config file> --gNBs.[0].min_rxtxtime 2 --sa --usrp-tx-thread-config 1 -E --continuous-tx
```

### 4.2 Run Quectel UE: [script](scripts/quectel_at.py)
```
sudo -E python3 quectel_at.py --interface <inetface_of_quectel> --port_location </dev/ttyUSBX>
```
