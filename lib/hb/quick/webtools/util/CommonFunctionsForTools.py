import urllib


def validateURLs(urls):
    for url in urls:
        urlError = validateURL(url)
        if urlError:
            return urlError


def validateURL(url):
    try:
        filehandle=urllib.urlopen(url)
        code = filehandle.getcode()
        if code != 200 and filehandle.url[:filehandle.url.find('://')] not in ['sftp', 'ftp', 'file']:
            return "Url: " + url + " did not return a file, HTTP code="+str(code)
    except IOError, e:
        return "Url: %s was not accepted as a valid URL. Error: %s" % (url, str(e))

        
def processIndicesString(rowIndicesStr):
    """
    Get list of 0-indexed indices from a string input (1-indexed, end inclusive)
    e.g.
    1-10, 13, 19 -> [0,1,2,3,4,5,6,7,8,9,12,18]
    """
    selectedIndices = []
    for indexPart in rowIndicesStr.split(','):
        if '-' in indexPart:
            startIndex, endIndex = [int(x.strip()) for x in indexPart.split('-')]
            selectedIndices += range(startIndex - 1, endIndex)
        else:
            selectedIndices.append(int(indexPart.strip()) - 1)  # assuming single value
    return selectedIndices
