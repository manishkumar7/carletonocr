import os
import OCR
import cv

segmenter = OCR.ConnectedComponentSegmenter()

allfiles = os.walk('/tmp/ocr')
dirs = []
results = {}
for i in allfiles:
    dirs.append(i)

for directory in dirs[1:10]:
    for image in directory[2]:
        print directory[0]+'/'+image
        im = cv.LoadImage(directory[0]+'/'+image, cv.CV_LOAD_IMAGE_GRAYSCALE)
        results[directory[0]+'/'+image] =  segmenter.segment(im)
        

print "Done"
