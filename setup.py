﻿# coding = utf-8

import json
import sys
import tempfile
import shutil
from os import path, remove, environ
from glob import glob
from setuptools import setup

with open('geosoft/pkg_info.json') as fp:
    _info = json.load(fp)

def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

version_tag = "{}{}".format(_info['version'], _info['pre-release'])

if _info['pre-release'] == '':
    dev_status_classifier = "Development Status :: 5 - Production/Stable"
else:
    dev_status_classifier = "Development Status :: 4 - Beta"


for f in glob("geosoft/*.pyd"):
    remove(f)


def is_arcgispro_build():
    if '--arcpy_build' in sys.argv:
        print("arcpy")
        index = sys.argv.index('--arcpy_build')
        sys.argv.pop(index)  # Removes the '--arcpy_build'
        return True

    conda_default_env = environ.get('CONDA_DEFAULT_ENV', None)
    if conda_default_env:
        return conda_default_env.endswith('arcgispro-py3')
    else:
        return False

if is_arcgispro_build():
    deps = [ ]
    shutil.copyfile('gxapi_arcpy.pyd', 'geosoft/gxapi.pyd')
else:
    deps = [ 'numpy>=1.11', 'pandas' ]
    if 'bdist_wheel' in sys.argv:
        # Have to specify python-tag to specify which module
        for arg in sys.argv:
            if arg.startswith('--python-tag='):
                pythontag = arg[13:]
                if pythontag == "cp34":
                    shutil.copyfile('gxapi.cp34-win_amd64.pyd', 'geosoft/gxapi.pyd')
                elif pythontag == "cp35":
                    shutil.copyfile('gxapi.cp35-win_amd64.pyd', 'geosoft/gxapi.pyd')
                elif pythontag == "cp36":
                    shutil.copyfile('gxapi.cp36-win_amd64.pyd', 'geosoft/gxapi.pyd')
                break
    else:
        # Copy the version we are building for
        py_ver_major_minor = sys.version_info[:2]
        if py_ver_major_minor == (3,4):
            shutil.copyfile('gxapi.cp34-win_amd64.pyd', 'geosoft/gxapi.pyd')
        elif py_ver_major_minor == (3,5):
            shutil.copyfile('gxapi.cp35-win_amd64.pyd', 'geosoft/gxapi.pyd')
        elif py_ver_major_minor == (3,6):
            shutil.copyfile('gxapi.cp36-win_amd64.pyd', 'geosoft/gxapi.pyd')

key_file = path.join('geosoft', 'geosoft.key')
with open(key_file, 'w') as f:
    use_default_key = True
    for arg in sys.argv:
        if arg.startswith('--use_geosoft_key='):
            index = sys.argv.index(arg)
            sys.argv.pop(index)  # Removes the arg
            geosoft_key = arg[18:]
            f.write(geosoft_key)
            use_default_key = False
            break
    if use_default_key:
        f.write("Core")


setup(
    name='geosoft',
    version=version_tag,
    description='Geosoft GX API module for Python',
    long_description=read('README.rst'),
    author='Geosoft Inc.',
    author_email='support@geosoft.com',
    platforms=["win_amd64"],
    url='https://github.com/GeosoftInc/gxpy',
    license='BSD',
    install_requires=deps,
    packages=[
        'geosoft',
        'geosoft.gxpy'
    ],
    package_data={ 'geosoft': ['geosoft.key', 'gxapi.pyd', '*.dll', '*.json', '*.zip'] },
    test_suite="geosoft.gxpy.tests",
    classifiers=[
        dev_status_classifier,
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
    ],
    )

