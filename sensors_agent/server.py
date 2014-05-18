import SocketServer
import subprocess
import shlex
import sensors
import json
import re


def get_sensors_temp():
    temp = {}
    chips = sensors.iter_detected_chips()
    for chip in chips:
        features = {}
        for feature in chip:
            # temperature type is 2
            if feature.type == 2:
                features[feature.label] = feature.get_value()
        if features:
            temp[str(chip)] = features

    return temp


def get_hdds():
    # ls /dev | grep sd
    ls = "ls /dev"
    grep = "grep sd"
    ls_process = subprocess.Popen(shlex.split(ls), stdout=subprocess.PIPE)
    grep_process = subprocess.Popen(shlex.split(grep), stdin=ls_process.stdout, stdout=subprocess.PIPE)

    out, err = grep_process.communicate()
    partitions = [line for line in out.split("\n") if line]
    hdds = [partition for partition in partitions if len(partition) == 3]
    return hdds


def get_hdd_temp(hdd):
    hddtemp = "hddtemp /dev/%s" % hdd
    grep = "grep ^/dev/%s" % hdd
    hddtemp_process = subprocess.Popen(shlex.split(hddtemp), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    grep_process = subprocess.Popen(
        shlex.split(grep),
        stdin=hddtemp_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    out, err = grep_process.communicate()
    parts = [line.rstrip().lstrip() for line in out.split(":")]
    try:
        value = float(parts[2].split(' ')[0])
    except ValueError:
        value = parts[2]
    return parts[1], value


def get_hdds_temp():
    temp = {}
    temp['hdd'] = {}
    hdds = get_hdds()
    for hdd in hdds:
        name, value = get_hdd_temp(hdd)
        temp['hdd'][name] = value
    return temp


class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        temp_sensors = get_sensors_temp()
        temp_hdd = get_hdds_temp()

        self.request.sendall(json.dumps(dict(temp_sensors.items() + temp_hdd.items())))


class Server(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, host, port):
        server_address = (host, port)
        SocketServer.ThreadingTCPServer.__init__(self, server_address, Handler)