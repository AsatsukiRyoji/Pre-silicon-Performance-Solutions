#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Methodology Log
@author: Li Lizhao
"""
import os,sys,logging
from util import get_now

class PMLog:

    def __init__(self, name=get_now(), path='./', level='info', timestamp=True):
        '''Performance Methodology Logger. Default is file log
        :name: log file name
        :path: where to store it. DEFAULT: ./
        :level: message level of log file
        '''
        ##How to use logging module
        #1)Define a logger which is a component on controlling send. 'DEBUG' logger 
        #can send out every message. 
        #2)Add handler to connect to this logger, like file or console handler. 
        #The handlers control receiving. Set them to wanted level to make messages above 
        #set level can be displayed. Like set file handler to 'WARNING(30)', messages 
        #from logger which have WARNING/ERROR/CRITICAL(FATAL) can be logged in the file
        #3)When use it, calling the logger.info/warning/... directly to control it send 
        #out messges have wanted level to file and/or console which will choose to accept 
        #them or not per their own message controlling level
        #3.1)On every calling, the handler will be added at first and removed after usage 
        #to assure only desired messages are sent on right time

        msgLv = {'debug':logging.DEBUG,     #10
                'info':logging.INFO,        #20
                'warning':logging.WARNING,  #30
                'error':logging.ERROR,      #40
                'fatal':logging.FATAL,      #50
                'critical':logging.CRITICAL #50
                }.get(level)
        if timestamp:
            self.fmt = logging.Formatter('%(asctime)s %(levelname)s\n%(message)s', '%d%H%M')
        else:
            self.fmt = logging.Formatter('%(levelname)s\n%(message)s')
        log_name = path+name+'.log'
        if os.path.exists(log_name):
            os.rename(log_name, log_name+'.old')
        self.logger= logging.getLogger(name)
        self.logger.setLevel(msgLv) #logging.DEBUG)
        ##file handler setting
        self.fh=logging.FileHandler(log_name)
        self.fh.setLevel(msgLv)
        self.fh.setFormatter(self.fmt)
        self.logger.addHandler(self.fh)
        ##console handler setting
        self.ch = logging.StreamHandler()
        self.ch.setLevel(msgLv) #logging.ERROR)
        self.ch.setFormatter(self.fmt)
        self.logger.addHandler(self.ch)

    def __addh(self):
        """Adding handlers before logger invoked because 
        they'd be removed by previous invocation of __rmvh
        """
        self.logger.addHandler(self.fh)
        self.logger.addHandler(self.ch)
    
    def __rmvh(self):
        """logging.shutdown() doesn't remove handler which 
        introduce duplicating message issues
        """
        self.logger.removeHandler(self.fh)
        self.logger.removeHandler(self.ch)
        self.logger.handlers = []

    def debug(self, msg):
        self.__addh()
        self.logger.debug(msg)
        self.__rmvh()

    def info(self, msg):
        self.__addh()
        self.logger.info(msg)
        self.__rmvh()
     
    def warning(self, msg):
        self.__addh()
        self.logger.warning(msg)
        self.__rmvh()

    def error(self, msg):
        self.__addh()
        self.logger.error(msg)
        self.__rmvh()

    def fatal(self, msg):
        self.__addh()
        self.logger.fatal(msg)
        self.__rmvh()

    def critical(self, msg):
        self.__addh()
        self.logger.critical(msg)
        self.__rmvh()

