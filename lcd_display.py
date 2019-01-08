#!/usr/bin/python

# PiVPN LCD Display Script
# By: Zeroward
# Requires I2C_LCD_Driver to fucntion
# Displays Local IP, Remote IP, Version number, and soon to be connections established
# As well as whatever else you want
# Shoutout to the Recon Sentinel Team for "letting" me tear their device apart
# and using it as a shitty VPN concentrator

import I2C_LCD_driver
from time import *
from urllib2 import urlopen
import socket
import fcntl
import struct


# Gets Local IP Address
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
        )[20:24])


# Fixes issue where some characters will persist after line changes, forces refresh of screen
def refresh_screen():
    mylcd.lcd_display_string("                     ",1)
    mylcd.lcd_display_string("                     ",2)


def display(k, v):
    mylcd.lcd_display_string(k, 1)
    mylcd.lcd_display_string(v, 2)


def read_pivpn_config():
    config = "/etc/pivpn/setupVars.conf"
    with open(config) as f:
        a = f.readlines()
        for i in a:
            if "PORT" in i:
                port = i.split("=")
                port = port[1]
                continue
            elif "PUBLIC" in i:
                public_dns = i.split("=")
                public_dns = public_dns[1]
                continue
            elif "IPv4addr" in i:
                ipv4_addr = i.split("=")
                ipv4_addr = ipv4_addr[1]
                continue
    return port.strip(), public_dns.strip(), ipv4_addr.strip()


def connection_monitor():
    connections = 0
    status_log = "/var/log/openvpn-status.log"
    with open(status_log) as f:
        for i in f.readlines():
            if "CLIENT_LIST" in i:
                connections += 1
    if connections == 0:
        return "No Connections"
    elif connections != 0:
        return str(connections)


# Time to declare us some globals
mylcd = I2C_LCD_driver.lcd() # LCD Screen Object 
my_remote_ip = urlopen('http://ip.42.pl/raw').read() # Get Remote IP
vpn_port, my_public_dns, my_local_ip = read_pivpn_config()
display_dictionary = {
        "PiVPN Display" : "Version .69",
        "Local IP:" : my_local_ip,
        "Remote IP:" : my_remote_ip,
        "Public DNS:" : my_public_dns,
        "VPN Port:" : vpn_port,
        "VPN Connections:" : connection_monitor(),
}
sleep_wait = 5 # Global Sleep Timer

def main():
    connection_monitor()
    while True:
        for k,v in display_dictionary.items():
            display(k,v)
            sleep(sleep_wait)
            refresh_screen()


if __name__ == "__main__":
    main()
