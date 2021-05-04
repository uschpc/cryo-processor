#!/usr/bin/python3

import os
import configparser
import logging

logger = logging.getLogger('cryoem')

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
            config_file_path = os.path.join(os.environ['HOME'], '.cryoem.conf')
            logger.info('Reading config from {}'.format(config_file_path))
            configparser.ConfigParser.__init__(self, interpolation=EnvInterpolation())
            try:
                self.read_file(open(config_file_path), 'r')
            except Exception:
                raise




