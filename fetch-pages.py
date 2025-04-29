import urllib.request, urllib.error, urllib.parse
import multiprocessing
import lxml.html
import os
import time


def cachedFetch(url, localPath, verbose=True):
    if os.path.exists(localPath):
        return 'Cached ' + url
    try:
        os.makedirs(os.path.split(localPath)[0])
    except OSError:
        pass
    if verbose:
        print('Fetching %s ...' % url)
    finished=False
    sleepTime=1
    while not(finished):
      try:
        response = urllib.request.urlopen(url)
        data = response.read()
        finished=True
      except:
        time.sleep(sleepTime)
        sleepTime*=2
        print('Fetching Hit a snag fetching the page, retrying... %s' % url)
    with open(localPath, 'wb') as f:
        f.write(data)
    return 'Fetched ' + url

def cachedRead(url, localPath):
    cachedFetch(url, localPath)
    return open(localPath, 'rb')
    
def mpFetch(args):
    return cachedFetch(*args, verbose=False)

def iterateAllPageURLs():
    with cachedRead('http://www.spec.org/cpu95/results/cint95.html', os.path.join('scraped', 'cint95.html')) as f:
        print('Scanning cint95.html ...')
        doc = lxml.html.parse(f)
    for elem, attr, link, pos in doc.getroot().iterlinks():
        if link.lower().endswith('.asc') or link.lower().endswith('.html'):
            yield 'http://www.spec.org' + link, os.path.join('scraped', 'cint95', link.split('/')[-1])

    with cachedRead('http://www.spec.org/cpu2000/results/cint2000.html', os.path.join('scraped', 'cint2000.html')) as f:
        print('Scanning cint2000.html ...')
        doc = lxml.html.parse(f)
    for elem, attr, link, pos in doc.getroot().iterlinks():
        if link.lower().endswith('.asc'):
            yield 'http://www.spec.org/cpu2000/results/' + link, os.path.join('scraped', 'cint2000', link.split('/')[-1])

    with cachedRead('http://www.spec.org/cpu2006/results/cint2006.html', os.path.join('scraped', 'cint2006.html')) as f:
        print('Scanning cint2006.html ...')
        doc = lxml.html.parse(f)
    for elem, attr, link, pos in doc.getroot().iterlinks():
        if link.lower().endswith('.txt'):
            yield 'http://www.spec.org/cpu2006/results/' + link, os.path.join('scraped', 'cint2006', link.split('/')[-1])

    with cachedRead('http://www.spec.org/cpu2017/results/cint2017.html', os.path.join('scraped', 'cint2017.html')) as f:
        print('Scanning cint2017.html ...')
        doc = lxml.html.parse(f)
    for elem, attr, link, pos in doc.getroot().iterlinks():
        if link.lower().endswith('.txt'):
            yield 'http://www.spec.org/cpu2017/results/' + link, os.path.join('scraped', 'cint2017', link.split('/')[-1])


if __name__ == '__main__':
    allPageURLs = list(filter(lambda x: "content" not in x[0] and "permute" not in x[0], list(iterateAllPageURLs())))
    pool = multiprocessing.Pool(64)
    i = 0
    for result in pool.imap_unordered(mpFetch, allPageURLs):
        i += 1
        print('%d/%d ... %s' % (i, len(allPageURLs), result))
