#!/usr/bin/env python
''' python interface to google translate '''

import json, os, socket, urllib
from urllib2 import Request, urlopen

def getlangs():
    ''' get the list of language codes, crappily '''
    req = Request('http://translate.google.com',
                   headers={'User-Agent' : 'Mozilla/4.0' })
    o = urlopen(req).read().split('<')
    langs = {}
    for i in o:
        if 'auto' in i or 'separator' in i:
            continue
        if 'value="' in i and 'option' in i:
            i = i.split('"')
            langs[i[-2]] =  i[-1][1:]
    return langs

def translate(string, inlang, outlang, referer=socket.gethostname()):
    ''' translate some text '''
    if not outlang:
        try:
            outlang = os.environ.get('LANG')[:2]
        except:
            return 'Error: no outbound language specified'
    data = { 'q' : string,
             'langpair' : '%s|%s' % (inlang, outlang),
             'v' : '1.0', }
    req = Request('http://ajax.googleapis.com/ajax/services/language/translate',
                  headers={'Referer' : referer})
    try:
        resp = json.loads(urlopen(req, data=urllib.urlencode(data)).read())
    except:
        return 'Error: couldn\'t get json'
    if 'responseData' not in resp:
        return 'Error: no responseData'
    if 'responseStatus' not in resp:
        return 'Error: no responseStatus'
    if resp['responseStatus'] != 200:
        return 'Error: responseStatus not 200 [%s]' % resp['responseStatus']
    return resp['responseData']['translatedText']

if __name__ == '__main__':

    import sys
    from optparse import OptionParser

    usage = '''
    shell interface to google translate

    glx [-i INLANG] [-o OUTLANG] STRING
    echo STRING | glx glx [-i INLANG] [-o OUTLANG]

    if outlang is not specified, tries to use $LANG
    if inlang is not specified, autodetect attempted
    '''

    parser = OptionParser(usage=usage)
    parser.add_option('-i', '--inlang', default='', help='language in')
    parser.add_option('-o', '--outlang', default='', help='language out')
    opts, args = parser.parse_args()
    if not args:
        args = sys.stdin.read().strip()
    else:
        args = ' '.join(args)

    print translate(args, opts.inlang, opts.outlang)
