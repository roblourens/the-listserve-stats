import os
import re
import operator
import yaml

def sortAndWrite(d, fileName):
    f = open(fileName, 'w')
    sortedD = sorted(d.iteritems(), key = lambda v: str('%06d_%06d' % (v[1], len(v[0]))), reverse = True)
    for item in sortedD:
        f.write(str('%s: %s\n' % (item[0], item[1])))

    f.close()

def filterAndWrite(d, n, fileName):
    f = open(fileName, 'w')
    items = list(d.iteritems())
    items = filter(lambda x: len(x[0]) >= n, items)
    sortAndWrite(dict(items), fileName)

def removeAll(strs, text):
    for s in strs:
        text = text.replace(s, ' ')

    return text

numWords = []
minWords = 10000
maxWords = 0
minWordNames = []
maxWordNames = []
def countAvgWords(text, postName):
    global minWords, maxWords, minWordName, maxWordName
    postWords = text.split()
    numPostWords = len(postWords)
    numWords.append(numPostWords)

    if numPostWords < minWords:
        minWords = numPostWords
        minWordName = [postName]
    elif numPostWords == minWords:
        minWordName.append(postName)

    if numPostWords > maxWords:
        maxWords = numPostWords
        maxWordName = [postName]
    elif numPostWords == maxWords:
        maxWordName.append(postName)

def addAndIncrement(k, d):
    if not d.has_key(k):
        d[k] = 0

    d[k] += 1

def countNWords(text, d, n):
    postWords = text.split()
    for i in range(len(postWords) - (n - 1)):
        addAndIncrement(' '.join(postWords[i : i+n]), d)

word2Freqs = {}
word3Freqs = {}
word4Freqs = {}
word5Freqs = {}
word6Freqs = {}
word7Freqs = {}
wordFreqs = {}
def countWords(text):
    postWords = text.split()
    for w in postWords:
        if w.find('@') >= 0:
            continue
        
        w = w.lower()
        w = w.rstrip('.')
        w = w.rstrip(',')

        addAndIncrement(w, wordFreqs)

locFreqs = {}
cityFreqs = {}
def countLocs(loc):
    # Discard email addresses
    if loc.find('@') >= 0:
        return

    # Discard > 4 words - probably not a location
    if len(loc.split()) > 4:
        return
    
    addAndIncrement(loc, locFreqs)

    city = loc.split(',')[0]
    addAndIncrement(city, cityFreqs)

def removeAll(strs, text):
    for s in strs:
        text = text.replace(s, ' ')

    return text

def removeTrailingTags(text):
    text = text.rstrip()
    while True:
        if text.endswith('<p>'):
            text = text.rpartition('<p>')[0]

        elif text.endswith('</p>'):
            text = text.rpartition('</p>')[0]

        elif text.endswith('<br />'):
            text = text.rpartition('<br />')[0]

        else:
            origText = text
            text = text.rstrip()
            if origText == text:
                break

    return text

postsPath = 'the-listserve-archive/_posts'
replaceWithSpace = ["<p>", "</p>", "\\n", "<br />", ":", '"', "!", "?", "...", "..", "(", ")", "-", "[", "]", "{", "}", "/", "\\", " '", "' "]
def processFile(postName):
    f = open(os.path.join(postsPath, postName), 'r')
    text = f.read().rstrip('-\n')
    data = yaml.safe_load(text)
    postText = data['api_data']['post_html']['body']

    postText = removeTrailingTags(postText)
    loc = postText[postText.rfind('>') + 1 :]
    countLocs(loc)

    postText = removeAll(replaceWithSpace, postText)
    postText = postText.replace("&#8217;", "'")
    postText = postText.replace("&#8216;", "'")
    postText = postText.replace("&#8220;", "'")
    postText = postText.replace("&#8221;", "'")
    postText = re.sub(r"&#\d*;", "", postText)

    countAvgWords(postText, postName)
    countWords(postText)
    countNWords(postText, word2Freqs, 2)
    countNWords(postText, word3Freqs, 3)
    countNWords(postText, word4Freqs, 4)
    countNWords(postText, word5Freqs, 5)
    countNWords(postText, word6Freqs, 6)
    countNWords(postText, word7Freqs, 7)

numFiles = 0
for postName in os.listdir(postsPath):
    if (postName.endswith('.html')):
        processFile(postName)
        numFiles += 1

sortAndWrite(wordFreqs, 'wordFreqs.txt')
sortAndWrite(cityFreqs, 'cityFreqs.txt')
sortAndWrite(locFreqs, 'locFreqs.txt')
sortAndWrite(word2Freqs, 'word2Freqs.txt')
sortAndWrite(word3Freqs, 'word3Freqs.txt')
sortAndWrite(word4Freqs, 'word4Freqs.txt')
sortAndWrite(word5Freqs, 'word5Freqs.txt')
sortAndWrite(word6Freqs, 'word6Freqs.txt')
sortAndWrite(word7Freqs, 'word7Freqs.txt')

filterAndWrite(wordFreqs, 4, 'wordFreqs-4.txt')
filterAndWrite(wordFreqs, 5, 'wordFreqs-5.txt')
filterAndWrite(wordFreqs, 6, 'wordFreqs-6.txt')

print('avg: ' + str(sum(numWords)/numFiles))
print('min: ' + str(minWords))
print('\t' + str(minWordName))
print('max: ' + str(maxWords))
print('\t' + str(maxWordName))
print('median: ' + str(sorted(numWords)[len(numWords)/2]))