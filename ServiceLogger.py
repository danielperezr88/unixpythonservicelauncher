# -*- coding: utf-8 -*-
"""
Created on Thu May 26 12:26:13 2016

@author: Dani
"""

from logging.handlers import RotatingFileHandler
from logging import Formatter, getLogger, DEBUG
import os
from utils import retrCwd, maybeCreateDirs


class ServiceLogger:

    def __init__(self, log, name, kind):
        logfile = os.path.join(retrCwd(), "logs", log)
        maybeCreateDirs(os.path.dirname(logfile))
        handler = RotatingFileHandler(logfile, maxBytes=1048576, backupCount=10)  # maxBytes = 1024^2
        formatter = Formatter('[' + kind + "]\t%(asctime)s\t%(name)-15s\t%(levelname)-7.7s\t%(message)s",
                              "%d-%m-%Y %H:%M:%S")
        handler.setFormatter(formatter)
        self.logger = getLogger(name)
        self.logger.handlers = []
        self.logger.addHandler(handler)
        self.logger.setLevel(DEBUG)

    def __del__(self):
        del self.logger

    def log(self, message):
        self.logger.info(message)
