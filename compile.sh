#!/bin/bash

mkdir dist
cd icons; ./compile.sh 
cd ..
Python setup.py py2app 
hdiutil create -imagekey zlib-level=9 -srcfolder dist/LogHound.app dist/LogHound.dmg


