#!/usr/bin/python
# coding=utf-8

"""
Actions - user defined actions

© Delaney & Morgan Computing 2019
www.delaneymorgan.com.au
"""

import time


def do_arrivals(manifest):
    ACTIVE_ON_OCCUPIED = [
        "amplifier",
        "chargers",
        "office_stereo",
        "sub_woofer"
    ]
    for name in ACTIVE_ON_OCCUPIED:
        instance = manifest.instance(name)
        if not instance.state():
            instance.turn_on()
    return


def do_departures(manifest):
    DEACTIVATE_ON_DEPARTURE = [
        "amplifier",
        "chargers",
        "lounge_tv",
        "office_stereo",
        "sub_woofer"
    ]
    for name in DEACTIVATE_ON_DEPARTURE:
        instance = manifest.instance(name)
        if instance.state():
            instance.turn_off()
    return


ACTIONS = {"do_arrivals": do_arrivals, "do_departures": do_departures}
