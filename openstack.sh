#!/bin/bash
while ! ansible-playbook openstack.yaml --tags lxd; do
	sleep 5s
done
lxc exec openstack -- apt update
lxc exec openstack -- apt dist-upgrade -y
lxc exec openstack -- apt install squashfuse -y
lxc exec openstack -- apt --purge -y remove lxd lxc-common lxcfs lxd-client
lxc exec openstack -- ln -sf /bin/true /usr/local/bin/udevadm
lxc exec openstack -- snap install conjure-up --classic --candidate
lxc exec openstack -- snap install lxd --edge
sleep 5s
lxc exec openstack -- lxd init --network-address=0.0.0.0 --network-port=8443 --storage-backend=dir --auto
lxc exec openstack -- lxc network create lxdbr0 ipv6.address=none ipv4.address=10.0.3.1/24 ipv4.nat=true
lxc exec openstack -- sudo -u ubuntu -i conjure-up --apt-proxy http://cache:3142 --apt-https-proxy http://cache:3142
