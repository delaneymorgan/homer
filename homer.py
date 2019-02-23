#!/usr/bin/python
# coding=utf-8


import argparse
import json
import os
import pyping
import random
import sys
import threading
import time

from actions import ACTIONS
from periodic import Periodic
from sharedvar import SharedVarCollection
from config import HomerConfig


__VERSION__ = "1.0.0"

CONFIG_FILENAME = "config.ini"


# =============================================================================


class Notifier(object):
    def __init__(self, args):
        self._args = args
        return

    def note(self, string):
        if self._args.verbose or self._args.diagnostic:
            print(string)
        return

    def warning(self, string):
        print("Warning: %s" % string)
        return

    def error(self, string):
        print("Error: %s" % string)
        return

    def diagnostic(self, string):
        if self._args.diagnostic:
            print("Diagnostic: %s" % string)
        return

    def fatal(self, string):
        print("Fatal: %s" % string)
        sys.stdout.flush()  # force print to flush
        # noinspection PyProtectedMember
        os._exit(1)
        return


# =============================================================================


class Channel(object):
    def __init__(self, name):
        self._name = name
        return

    def authenticate(self):
        raise NotImplementedError()


# =============================================================================


class PhilipsHueChannel(object):
    def __init__(self, name):
        super(PhilipsHueChannel, self).__init__(name)
        self._name = name
        return

    def authenticate(self):
        raise NotImplementedError()


# =============================================================================


class Switch(object):
    def __init__(self, name, address):
        self._name = name
        self._address = address
        return

    def turn_on(self):
        raise NotImplementedError()

    def turn_off(self):
        raise NotImplementedError()

    def _actual_state(self):
        raise NotImplementedError()

    def state(self):
        raise NotImplementedError()


# =============================================================================


class Feibit(Switch):
    def __init__(self, name, address):
        super(Feibit, self).__init__(name, address)
        self._state = self._actual_state()
        return

    def turn_on(self):
        print("turning %s on" % self._name)
        self._state = True
        return

    def turn_off(self):
        print("turning %s off" % self._name)
        self._state = False
        return

    def _actual_state(self):
        # get state of device from device itself
        return False

    def state(self):
        return self._state


# =============================================================================


class Wemo(Switch):
    def __init__(self, name, address):
        super(Wemo, self).__init__(name, address)
        self._state = self._actual_state()
        return

    def turn_on(self):
        print("turning %s on" % self._name)
        self._state = True
        return

    def turn_off(self):
        print("turning %s off" % self._name)
        self._state = False
        return

    def _actual_state(self):
        # get state of device from device itself
        return False

    def state(self):
        return self._state


# =============================================================================


class SamsungTV(Switch):
    def __init__(self, name, address):
        super(SamsungTV, self).__init__(name, address)
        self._state = self._actual_state()
        return

    def turn_on(self):
        print("turning %s on" % self._name)
        self._state = True
        return

    def turn_off(self):
        print("turning %s off" % self._name)
        self._state = False
        return

    def _actual_state(self):
        # get state of device from device itself
        return False

    def state(self):
        return self._state


# =============================================================================


class Light(object):
    def __init__(self, name, address):
        self._name = name
        self._address = address
        return

    def turn_on(self):
        raise NotImplementedError()

    def turn_off(self):
        raise NotImplementedError()

    def _actual_state(self):
        raise NotImplementedError()

    def state(self):
        raise NotImplementedError()


# =============================================================================


class Hue(Light):
    def __init__(self, name, address):
        super(Hue, self).__init__(name, address)
        self._state = self._actual_state()
        return

    def turn_on(self):
        print("turning %s on" % self._name)
        self._state = True
        return

    def turn_off(self):
        print("turning %s off" % self._name)
        self._state = False
        return

    def _actual_state(self):
        # get state of device from device itself
        return False

    def state(self):
        return self._state


# =============================================================================


# TODO: load this info from config file
DEVICE_MANIFEST = dict(
    amplifier          = dict(address="192.168.1.240", room="lounge",  type="Feibit"),
    craig_mobile       = dict(address="192.168.1.230",                 type="mobile"),
    bedroom_lamp_leftr = dict(address="hue:01",        room="lounge",  type="Hue"),
    bedroom_lamp_right = dict(address="hue:02",        room="lounge",  type="Hue"),
    chargers           = dict(address="192.168.1.243", room="library", type="Wemo"),
    kylie_mobile       = dict(address="192.168.1.231",                 type="mobile"),
    lounge_lamp_leftr  = dict(address="hue:03",        room="lounge",  type="Hue"),
    lounge_lamp_right  = dict(address="hue:04",        room="lounge",  type="Hue"),
    lounge_tv          = dict(address="192.168.1.243", room="lounge",  type="SamsungTV"),
    office_stereo      = dict(address="192.168.1.241", room="office",  type="Feibit"),
    sub_woofer         = dict(address="192.168.1.242", room="office",  type="Wemo"),
)


# =============================================================================


class Manifest(object):
    def __init__(self, device_manifest, managed_devices, notifier):
        self._device_manifest = device_manifest
        self._notifier = notifier
        self._managed_devices = {}
        for name in managed_devices:
            if name in device_manifest:
                info = device_manifest[name]
                tgt_class = info["type"]
                try:
                    constructor = globals()[tgt_class]
                    self._managed_devices[name] = constructor(name, info["address"])
                except KeyError as e:
                    self._notifier.fatal("%s requires %s class implementation in order to be managed" % (name, str(e)))
        return

    def instance(self, name):
        return self._managed_devices[name]

    def address(self, name):
        info = self._device_manifest[name]
        address = info["address"]
        return address


# =============================================================================


class Surveyor(threading.Thread):
    def __init__(self, args, manifest, monitored_devices, check_period, notifier):
        super(Surveyor, self).__init__()
        self._args = args
        self._manifest = manifest
        self._monitored_devices = monitored_devices
        self._notifer = notifier
        self._roll_call = SharedVarCollection({})
        self._devices_poll = Periodic(check_period, self.poll_devices, "poll_devices")
        return

    def poll_devices(self):
        for name in self._monitored_devices:
            self._notifer.diagnostic("pinging %s" % name)
            found = self.ping(self._manifest.address(name))
            if found:
                self._roll_call.set(name, True)
                self._notifer.note("%s found" % name)
            else:
                self._roll_call.set(name, False)
                self._notifer.note("%s missing" % name)
        return

    def ping(self, ip_address):
        # NOTE: ping requires root access.  Fake it during development with a random#
        if hasattr(args, 'test') and args.test:
            found = (random.randint(0, 3) == 3)
        else:
            response = pyping.ping(ip_address)
            found = (response.ret_code == 0)
        return found

    def roll_call(self):
        return self._roll_call.get()

    def check(self):
        self._devices_poll.check()
        return

    def run(self):
        while gRunningFlag:
            self._devices_poll.check()
        return


# =============================================================================


class Judge(object):
    def __init__(self, filename, surveyor, notifier):
        self._surveyor = surveyor
        self._notifier = notifier
        the_file = open(filename, "r")
        json_str = the_file.read()
        the_file.close()
        self._rules = json.loads(json_str)
        return

    def _evaluate_rule(self, rule):
        status = False
        _ = rule
        return status

    def make_rulings(self):
        self._notifier.note("evaluating rules")
        for this_rule in self._rules:
            self._notifier.diagnostic("evaluating: %s" % this_rule)
        return []


# =============================================================================


class Valet(object):
    def __init__(self, devices, surveyor, judge, actions, notifier):
        self._devices = devices
        self._surveyor = surveyor
        self._judge = judge
        self._actions = actions
        self._notifier = notifier
        return

    def check(self):
        required_actions = self._judge.make_rulings()
        self._notifier.note("actions required: %s" % required_actions)
        for action in required_actions:
            self._actions[action]()
        return


# =============================================================================


def arg_parser():
    """
    parse arguments

    :return: the parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Homer.')
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")
    parser.add_argument("-d", "--diagnostic", help="diagnostic mode (includes verbose)", action="store_true")
    parser.add_argument("-t", "--test", help="use fake pings for simulation", action="store_true")
    parser.add_argument("--version", action="version", version='%(prog)s {version}'.format(version=__VERSION__))
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    print("Homer start")
    args = arg_parser()
    notifier = Notifier(args)
    config = HomerConfig(CONFIG_FILENAME)
    managed_devices = config.devices_details()["managed_devices"]
    manifest = Manifest(DEVICE_MANIFEST, managed_devices, notifier)
    monitored_devices = config.devices_details()["monitored_devices"]
    # noinspection PyTypeChecker
    surveyor = Surveyor(args, manifest, monitored_devices, 15, notifier)
    rules_filename = config.general_details()["rules_filename"]
    judge = Judge(rules_filename, surveyor, notifier)
    valet = Valet(manifest, surveyor, judge, ACTIONS, notifier)
    # roll_caller.start()
    try:
        while True:
            surveyor.check()
            notifier.note("roll call: %s" % surveyor.roll_call())
            valet.check()
            time.sleep(5)
    except KeyboardInterrupt:
        gRunningFlag = False
        pass
    print("Homer end")
