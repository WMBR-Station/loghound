

SVGFILE=loghound.svg
BASEFILE=loghound

all:
	convert ${SVGFILE} -resize 16x16 ${BASEFILE}16.png
	convert ${SVGFILE} -resize 32x32 ${BASEFILE}32.png
	convert ${SVGFILE} -resize 48x48 ${BASEFILE}48.png
	convert ${SVGFILE} -resize 128x128 ${BASEFILE}128.png
	convert ${SVGFILE} -resize 256x256 ${BASEFILE}256.png
	convert ${SVGFILE} -resize 512x512 ${BASEFILE}512.png
	png2icns ${BASEFILE}.icns ${BASEFILE}16.png  ${BASEFILE}32.png ${BASEFILE}48.png ${BASEFILE}128.png ${BASEFILE}256.png ${BASEFILE}512.png
	rm -f ${BASEFILE}*.png 

clean:
	rm -f ${BASEFILE}*.png *.icns
