#!/bin/bash
virt-install --name kubernetes --ram 65536 --disk path=/var/lib/libvirt/images/kubernetes.qcow2,size=22 --vcpus 8 --os-type linux --os-variant generic --network bridge=virbr0 --graphics none --console pty,target_type=serial --location 'http://archive.ubuntu.com/ubuntu/dists/zesty/main/installer-amd64/' --extra-args 'console=ttyS0,115200n8 serial'
