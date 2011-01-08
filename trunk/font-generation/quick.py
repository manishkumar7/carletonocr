import cv
import sys

win_name = 'win'
im = cv.LoadImage(sys.argv[1])
cv.ShowImage(win_name, im)

input("")
