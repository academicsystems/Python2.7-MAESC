#!/usr/bin/python2.7

import warnings
warnings.filterwarnings("ignore")

import atexit
import cgi
import json
import mimetypes
import os
import random
import re
import shutil
import signal
import string
import time
import web
import zipfile
from types import ModuleType

# clean up tmp folder whenever this goes down

def exit_handler():
    folder = '/var/www/tmp'
    for file in os.listdir(folder):
        fpath = os.path.join(folder, file)
        try:
            if os.path.isfile(fpath):
                os.unlink(fpath)
            elif os.path.isdir(fpath):
                shutil.rmtree(fpath)
        except Exception as e:
            pass

atexit.register(exit_handler)

# variables for users

SAVE_DIR = '/var/www/tmp/'

# helper functions

def python_exec(pystr):
    try:
        import networkx
        import numpy
        import qanswer as qengine
        import scipy
        exec(pystr,locals())
    except IOError as e:
        qerr = 'Error, you must prefix all files to be saved with SAVE_DIR'
    except Exception as e:
        qerr = str(e)
    del pystr
    lvars = locals()
    pyvars = {}
    for key, obj in lvars.iteritems():
        if not isinstance(obj,ModuleType) and key != '__builtins__':
            pyvars[key] = obj
    return pyvars

def filter_vars(pyvars,reqkeys):
    reqvars = {}
    for key in reqkeys:
        if key in pyvars:
            reqvars[key] = pyvars[key]
	else:
            reqvars[key] = ''
    return reqvars

# web routes

mimetypes.init()

class Main:
    def POST(self):
        # get post request json body
        try:
            data = json.loads(web.data())
        except:
            respdict = {'error':['json is not formatted correctly']}
            return json.dumps(respdict)
        
        # execute sage commands
        try:
            pyvars = python_exec(data['code'])
            if 'qerr' in pyvars:
                return json.dumps({'error':[cgi.escape(pyvars['qerr'])]})
        except Exception as e:
            respdict = {'error':[cgi.escape(str(e))]}
            return json.dumps(respdict)
        
        # get requested variables
        reqvars = filter_vars(pyvars,data['vars'])
        
        respdict = {}
        for key, value in reqvars.iteritems():
            if key[0] != "_":
                respdict[key] = [str(value)]
            else:
                respdict[key] = [value]
        
        return json.dumps(respdict)

class TestConnection:
    def GET(self):
        startTime = time.time()
        python_exec('x = 1')
        totalTime = time.time() - startTime
        respdict = {'Python Exec Time':totalTime}
        return json.dumps(respdict)

# /service => responds with {reqvar:["text","latex"],filevar:["filename"]} etc.
if __name__ == "__main__":
    # symlink tmp directory for user generated files to static directory
    if os.path.exists('/var/www/static'):
        os.unlink('/var/www/static')
    try:
        os.symlink('/var/www/tmp','/var/www/static')
    except:
        pass
    
    urls = (
          '/service', 'Main',
          '/', 'TestConnection'
        )
    app = web.application(urls, globals())
    app.run()
