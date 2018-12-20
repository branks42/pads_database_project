#!/usr/bin/python

####################################################################################################
# Chris Sweet. Computer Science and Engineering. Notre Dame/CRC.
# 08/01/2014
# Separate QR and Marker points and remove additional points
####################################################################################################

# imports

import zbar
from PIL import Image, ImageEnhance

# scan and rectify image function


def scan_rectify_image(filename):
    # create a reader
    scanner = zbar.ImageScanner()

    # configure the reader
    scanner.parse_config('enable')

    # obtain image data
    # This converts image to greyscale
    pil = Image.open(filename).convert('L')
    # Enhance brightness, and contrast
    bright = ImageEnhance.Brightness(pil)
    pil = bright.enhance(1.0)
    contrast = ImageEnhance.Contrast(pil)
    pil = contrast.enhance(2.0)
    sharp = ImageEnhance.Sharpness(pil)
    pil = sharp.enhance(0.3)
    width, height = pil.size
    raw = pil.tobytes()
    # pil.save('tmp.png')

    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)

    # scan the image for barcodes
    scanner.scan(image)

    # extract results
    for symbol in image.symbols:
        # print what we have found
        # print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data

        # get serial number if exists
        loc = symbol.data.find("padproject.nd.edu/?s=")

        # did we get sn?
        if loc != -1:
            # seperate out the code
            serial_no = symbol.data[21:]

            return ("{}".format(serial_no))
