sudo ifconfig eth2 192.168.40.1
sudo ethtool -G eth2 tx 4096 rx 4096
sudo ip link set dev eth2 mtu 9000
