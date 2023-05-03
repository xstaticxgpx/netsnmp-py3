from setuptools import setup, Extension, find_packages
import os
import re
import sys

VERSION="0.6"

intree=0

_incdirs = ['./netsnmp']
_libdirs = []

args = sys.argv[:]
for arg in args:
    if '--basedir' in arg:
        basedir = arg.split('=')[1]
        sys.argv.remove(arg)
        intree=1
    if '--incdir' in arg:
        incdir = arg.split('=')[1]
        sys.argv.remove(arg)
        _incdirs.append(incdir)
    if '--libdir' in arg:
        libdir = arg.split('=')[1]
        sys.argv.remove(arg)
        _libdirs.append(libdir)


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
    libs = re.findall(r" -l(\S+)", netsnmp_libs)

# For _api.h references/travis-ci build
incdirs+=_incdirs
libdirs+=_libdirs

# Asynchronous IPC
libs.append('zmq')
libs.append('czmq')

setup(
    name="netsnmp-py",
    version=VERSION,
    description='Python NET-SNMP Bindings',
    author='Gabe Pacuilla',
    author_email='root@un1x.su',
    url='https://github.com/xstaticxgpx/netsnmp-py3',
    license='MIT License',
    download_url='https://github.com/xstaticxgpx/netsnmp-py3/archive/v%s.tar.gz' % VERSION,
    packages=find_packages(),
    ext_modules = [
       Extension("netsnmp._api",
                 ["netsnmp/session.c",
                  "netsnmp/get.c",
                  "netsnmp/get_async.c",
                  "netsnmp/interface.c",
                  "netsnmp/_api.c"],
                 library_dirs=libdirs,
                 include_dirs=incdirs,
                 libraries=libs)
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: C',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
)
