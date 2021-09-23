#!/usr/bin/python3

import os
import configparser
import logging

log = logging.getLogger('cryoem')

class EnvInterpolation(configparser.BasicInterpolation):
    '''Interpolation which expands environment variables in values.'''

    def before_get(self, parser, section, option, value, defaults):
        return os.path.expandvars(value)


class Config:
    # singleton
    instance = None

    def __init__(self):
        if not Config.instance:
            Config.instance = Config.__Config()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    class __Config(configparser.ConfigParser):

        def __init__(self):
            config_file_path = os.path.join(os.environ['HOME'], '.cryoem-dev.conf')
            log.info('Reading config from {}'.format(config_file_path))
            configparser.ConfigParser.__init__(self, interpolation=EnvInterpolation())
            try:
                self.read_file(open(config_file_path), 'r')
            except Exception:
                raise
            # base_dir is where this install is
            self.set("general", "base_dir", os.getcwd())
            log.info("Base directory of the install is {}".format(self.get("general", "base_dir")))




