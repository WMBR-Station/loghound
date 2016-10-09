

all: LogHound.app LogHound.dmg

dist:
	mkdir dist

icons/loghound.icns:
	cd icons; make

LogHound.app: icons/loghound.icns
	python setup.py py2app 

LogHound.dmg: LogHound.app dist 
	hdiutil create -imagekey zlib-level=9 -srcfolder dist/LogHound.app dist/LogHound.dmg

clean:
	rm -rf *.pyc dist build
	cd icons; make clean

