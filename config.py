"""
Homer Configuration Parser

Loads configuration from config.ini and produces a configuration dictionary.
"""


import configparser
import json
from enum import Enum


# =============================================================================


class Sections(Enum):
    GENERAL = 2
    DEVICES = 1


# Defines the various required configuration members and their types.
GENERAL_MEMBERS = {'rules_filename': 'string'}
DEVICES_MEMBERS = {'monitored_devices': 'list', 'managed_devices': 'list', 'rooms': 'list'}


# =============================================================================


class HomerConfig:
    config = {}

    # A list of parsers for given data types. Note that many are non-standard types that
    # we do special case handling for.
    configTypeParsers = {
        'dict': lambda self, settings, section, member: eval(settings.get(section, member)),
        'list': lambda self, settings, section, member: eval(settings.get(section, member)),
        'string': lambda self, settings, section, member: settings.get(section, member),
        'integer': lambda self, settings, section, member: settings.getint(section, member),
        'bool': lambda self, settings, section, member: settings.getboolean(section, member),
        'float': lambda self, settings, section, member: settings.getfloat(section, member),
    }

    def __init__(self, filename='config.ini'):
        self.filename = filename
        settings = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        settings.read(self.filename)

        self.config[Sections.GENERAL] = self.read_general(settings)
        self.config[Sections.DEVICES] = self.read_devices(settings)
        return

    def read_general(self, settings):
        general = {}
        for member in GENERAL_MEMBERS:
            general[member] = self.parse_general_member(settings, member, GENERAL_MEMBERS[member])
        return general

    def parse_general_member(self, settings, member, member_type):
        # noinspection PyUnresolvedReferences
        return self.parse_config_entry(settings, Sections.GENERAL.name, member, member_type)

    def read_devices(self, settings):
        devices = {}
        for member in DEVICES_MEMBERS:
            devices[member] = self.parse_devices_member(settings, member, DEVICES_MEMBERS[member])
        return devices

    def parse_devices_member(self, settings, member, member_type):
        # noinspection PyUnresolvedReferences
        return self.parse_config_entry(settings, Sections.DEVICES.name, member, member_type)

    def parse_config_entry(self, settings, section, member, member_type):
        return self.configTypeParsers[member_type](self, settings, section, member)

    def general_details(self):
        return self.config[Sections.GENERAL]

    def devices_details(self):
        return self.config[Sections.DEVICES]


# =============================================================================


if __name__ == "__main__":
    cfg = HomerConfig()
    print(json.dumps(cfg.config, indent=4))
