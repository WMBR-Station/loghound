

all: LogHound.app LogHound.dmg

dist:
	mkdir dist

icons:
	cd icons; make

LogHound.app:

LogHound.dmg: LogHound.app dist icons
	hdiutil create -imagekey zlib-level=9 -srcfolder dist/LogHound.app dist/LogHound.dmg

clean:
	rm -rf dist build
	cd icons; make clean

