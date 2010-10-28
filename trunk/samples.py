"""
Travis Raines
samples.py

Read the file 'list' in a given directory, containing newline-delimited strings.
Generate images in the same directory containing images of those strings in
the specified font.
This, of course, cannot handle multi-line strings, but I don't know how to
properly handle them anyway, since ImageDraw seems to put garbage where it
finds newlines.
"""

import Image, ImageDraw, ImageFont
import sys
import optparse

def main():
    options = getOptions()
    run(options.font, options.size, options.single)

def run(font, size, target, single=False, outdir=None):
    font = ImageFont.truetype(font, size)
    if not single:
        directory = target
        if directory[-1] != '/': directory += '/'
        
        try:
            words = open(directory + "list", "r")
        except IOError:
            print "No list file found! Exiting..."
            sys.exit(1)
    else: 
        words = [target]
        directory = "./"

    if outdir: directory = outdir
    for word in words:
        generateImage(word.strip(), directory, font)

def generateImage(word,directory,font):
    """
    Creates and saves an image of word typeset in font in directory.
    """

    # I don't know why ImageDraw requires you create the draw object
    # before figuring out how big it needs to be, but it does.
    im = Image.new("L", (20,20), 255)
    draw = ImageDraw.Draw(im)
    size = draw.textsize(word, font=font)
    im = im.resize(size)
    draw = ImageDraw.Draw(im)

    draw.text((0,0), word, font=font)
    filename = word.replace(' ','_') + '.png'
    im.save(directory + filename)

def getOptions():
  """
  Read in the command-line options and assign them to the appropriate places.
  Returns a parser object.
  """

  parser = optparse.OptionParser()

  parser.add_option("-f", "--font", action="store", dest="font",
          default="/usr/share/fonts/TTF/times.ttf",
          help="TrueType font to use. Default only works on Linux.")

  parser.add_option("-s", "--size", action="store", type="int", dest="size", default=32,
          help="Font size to use, in points.")

  parser.add_option("-o", "--single", action="store_true", dest="single", default=False,
          help="Interpret the argument as a single string, rather than \
          a directory with a list file.")

  (options, args) = parser.parse_args()

  # Sanity checks
  if not args:
    print "No directory specified, nothing to do. Exiting..."
    sys.exit(1)
  if len(args) > 1:
    print "Multiple directory specified or garbled input. Please specify only one file."
    sys.exit(1)

  # Because I really have no reason to return the single-item args by itself
  options.file = args[0]

  return options

if __name__ == "__main__":
    main()
