import cli
import ocr.OCR
import os
import sys
'''
Takes a directory as a command line argument and runs OCR on each image in the directory.
Every image must have a corresponding text file with the same name and a .txt extension
in the directory. OCR is run with using the feature extractors and linguists specified
directly below. The edit distance (using only insertions and deletions) and number of
letter correctly identfied are both calculated and written to a file for each run of 
the OCR algorithm.
'''
FEATURE_EXTRACTORS = ['histogram','template']
LINGUISTS = ['spelling','n-gram']

def getText(target):
	pLoc = target.index('.')
	name = target[:pLoc]
	textLoc = name+'.txt'
	try:
		file = open(textLoc)
	except:
		sys.stderr.write('Image requires a corresponding text file with the same name and a .txt extension\n')
		sys.exit(0)
	text = ''
	for l in file:
		text += l
	return text.strip()

def lettersIDed(guess,trueText):
	guess = guess.lower()
	trueText = trueText.lower()
	index = 0
	letters = 0
	for l in trueText:
		if l in guess[index:]:
			letters += 1
			index = guess[index:].index(l)
	return letters

def editDistance(str1,str2):
	d = []
	d.append([i for i in xrange(len(str2)+1)])
	for i in xrange(len(str1)):
		d.append([i+1]+[0 for x in xrange(len(str2))])
	for i in xrange(1,len(str1)+1):
		for j in xrange(1,len(str2)+1):
			if str1[i-1] == str2[j-1]:
				d[i][j] = d[i-1][j-1]
			else:
				d[i][j] = min(d[i-1][j]+1,d[i][j-1]+1)
	return d[-1][-1]

def writeStats(file, answers):
	out = file
	for a in answers:
		out.write('ACTUAL TEXT:\n'+a[0]+' '+str(len(a[0]))+'\n')
		out.write('BEST GUESS:\n'+a[1]+' '+str(len(a[1]))+'\n')
		out.write('FEATURE EXTRACTOR: '+a[2]+'\n')
		out.write('LINGUIST: '+a[3]+'\n')
		out.write('LETTERS IDENTIFIED: '+str(a[4])+'\n')
		out.write('PERCENT LETTERS IDENTIFIED: '+str(a[5])+'\n')
		out.write('EDIT DISTANCE: '+str(a[6])+'\n')
		out.write('\n')


if __name__ == '__main__':
	options, parser = cli.getOptions()
	dirName = options.target
	try:
		files = os.listdir(dirName)
	except:
		sys.stderr.write('tester.py takes in a directory name, not an image name\n')
		sys.exit(0)
	images = []
	for f in files:
		if f[-4:] == '.png' or f[-4:] == '.jpg':
			images.append(f)			
	for i in range(len(images)):
		print images[i]
		print images
		options.target = dirName+'/'+images[i]
		text = getText(options.target)
		outName = dirName+'/testResults_'+str(i)+'.txt'
		out = open(outName,'w')
		answers = []
		for f in FEATURE_EXTRACTORS:
			options.featureExtractor = f
			for l in LINGUISTS:
				options.linguist = l
				answer = ocr.OCRRunner().withOptions(options)
				print answer
				raw_input('enter')
				lIDed = lettersIDed(answer,text)
				percentlIDed = float(lIDed)/len(text) * 100
				eDist = editDistance(answer,text)
				a = [text,answer,f,l,lIDed,percentlIDed,eDist]
				answers.append(a)
		writeStats(out,answers)
		out.close()