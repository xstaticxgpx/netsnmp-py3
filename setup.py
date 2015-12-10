from distutils.core import setup, Extension
from setuptools import setup, Extension, find_packages
import os
import re
import sys

intree=0

args = sys.argv[:]
for arg in args:
    if '--basedir' in arg:
        basedir = arg.split('=')[1]
        sys.argv.remove(arg)
        intree=1

if intree:
    netsnmp_libs = os.popen(basedir+'/net-snmp-config --libs').read()
    libdir = os.popen(basedir+'/net-snmp-config --build-lib-dirs '+basedir).read()
    incdir = os.popen(basedir+'/net-snmp-config --build-includes '+basedir).read()
    libs = re.findall(r"-l(\S+)", netsnmp_libs)
    libdirs = re.findall(r"-L(\S+)", libdir)
    incdirs = re.findall(r"-I(\S+)", incdir)
else:
    netsnmp_libs = os.popen('net-snmp-config --libs').read()
    libdirs = re.findall(r"-L(\S+)", netsnmp_libs)
    incdirs = []
    libs = re.findall(r"-l(\S+)", netsnmp_libs)

# For _api.h references
incdirs.append('./netsnmp')

# Asynchronous IPC
libs.append('zmq')
libs.append('czmq')

setup(
    name="netsnmp", version="1.0a1",
    description = 'Python3 NET-SNMP Bindings',
    packages=find_packages(),

    ext_modules = [
       Extension("netsnmp._api",
                 ["netsnmp/session.c",
                  "netsnmp/get.c",
                  "netsnmp/getnext.c",
                  "netsnmp/get_async.c",
                  "netsnmp/interface.c",
                  "netsnmp/_api.c"],
                 library_dirs=libdirs,
                 include_dirs=incdirs,
                 libraries=libs )
       ]
    )
