# -*- coding: utf-8 -*-
"""
Created on Thu May 26 10:27:40 2016

@author: Dani
"""

import os
import glob
import re
import sys

from time import sleep

from utils import retrCwd

from importlib import import_module, reload, invalidate_caches

from tempfile import gettempdir as gettemp

from daemon import Daemon

from ServiceLogger import ServiceLogger

from services.ServiceException import LoggerException, ScheduleException, ScriptException


cwd = retrCwd()
os.chdir(os.path.dirname(cwd))
svcdir = os.path.join(cwd, "services")
sys.path.append(svcdir)


class ServiceLauncherDaemon(Daemon):
   
    _svc_name_ = "PySvcLauncher"
    _svc_display_name_ = "Lanzador de servicios python"
    _svc_description_ = "Servicio de gestión de ejecución de scripts de Python"
         
    def __init__(self, *args, **kwargs):
        Daemon.__init__(self, *args, **kwargs)
        self.logger = ServiceLogger("servicelauncher.log", "servicelauncher", 'ServiceLauncher')

    def log(self, message):
        self.logger.log(message)
         
    def run(self):
        instances = {}
        modules = {}
        while 1:

            """ Ok, here's the real money shot right here.
                [actual service code between rests]        """
            svcscripts = glob.glob(os.path.join(svcdir, "*Svc.py"))
            svcscripts = [re.split(r'[\\/]+', s)[-1] for s in svcscripts]

            for script in svcscripts:
                try:
                    if script not in modules.keys():
                        modules.update({script: import_module(script[:-3])})
                    else:
                        modules[script] = reload(modules[script])
                except Exception as x:
                    self.log("%s:%s - Error: %s at %d" %
                             (self._svc_name_, script, str(x), sys.exc_info()[-1].tb_lineno))
                    continue

            todel = []
            for script in [s for s in svcscripts if s not in instances.keys()]:
                try:
                    aux_class = getattr(modules[script], script[:-6])
                    instances.update({script: aux_class()})
                except Exception as x:
                    self.log("%s:%s - Error: %s at %d" %
                             (self._svc_name_, script, str(x), sys.exc_info()[-1].tb_lineno))
                    if script in instances.keys():
                        todel.append(script)  # Service will be forced to reload Script
                    continue
                self.log('"%s" Added to Script list' % (script,))

            if len(todel) > 0:
                for script in todel:
                    del instances[script]
                del todel
                invalidate_caches()

            for script in [s for s in instances.keys() if s not in svcscripts]:
                try:
                    del instances[script]
                except Exception as x:
                    self.log("%s:%s - Error: %s at %d" %
                             (self._svc_name_, script, str(x), sys.exc_info()[-1].tb_lineno))
                    continue
                self.log('"%s" Removed from Script list' % (script,))

            todel = []
            for script in instances.keys():
                try:
                    instances[script].run()
                except(ScriptException, LoggerException, ScheduleException) as x:
                    self.log(str(x))
                    todel.append(script)  # Service will be forced to reload Script
                    continue
                except Exception as x:
                    self.log("%s:%s - Error: %s at %d" %
                             (self._svc_name_, script, str(x), sys.exc_info()[-1].tb_lineno))
                    todel.append(script)  # Service will be forced to reload Script
                    continue

            if len(todel) > 0:
                for script in todel:
                    del instances[script]
                del todel
                invalidate_caches()

            sleep(60)

        """ [actual service code between rests] """

                  
if __name__ == '__main__':
    daemon = ServiceLauncherDaemon(os.path.join(gettemp(), 'daemon-example.pid'))
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % (sys.argv[0],))
        sys.exit(2)

