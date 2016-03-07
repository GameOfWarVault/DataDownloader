# -*- coding: utf-8 -*-
from __future__ import print_function
import urllib2
import sys
import json
import os.path
import io
import colorama
from multiprocessing import Pool

colorama.init()

MANIFEST_URL = 'http://206drody.mobboss-online.com/index.php?action=manifest&app_version=0&controller=file&dpi=2x&lang=en&layout=tablet&opcode=op1'
IXB_URL      = 'http://cdn-aws.mobboss-online.com/5087/_ixb/'
DOUBLE_URL   = 'http://cdn-aws.mobboss-online.com/5087/2x/'
TABLET_URL   = 'http://cdn-aws.mobboss-online.com/5087/tablet/'
DEF_URL      = 'http://cdn-aws.mobboss-online.com/5087/_def/'

MANIFEST_FILE = 'manifest.json'


class Response:
    NOT_RECOGNIZED = 0
    SKIPPED        = 1
    DOWNLOADED     = 2
    NOT_FOUND      = 3

class Asset(object):
    """docstring for Asset"""
    def __init__(self):
        super(Asset, self).__init__()
        


def read(filename):
    fp = open(filename, 'rb')
    try:
        ret = fp.read(-1)
        return ret
    finally:
        fp.close()


def write(data, filename):
    # with io.open(filename, 'w', encoding='utf-8') as f:
            # f.write(unicode(data))
    with io.open(filename, 'wb') as f:
        f.write(data)


def chunk_report(filename, bytes_so_far, total_size):
    message = "Downloading \"" + filename + "\""
    if total_size is None:
        sys.stdout.write(message + "...\r")
    else:
        percent = float(bytes_so_far) / total_size
        percent = round(percent * 100, 2)
        sys.stdout.write(message + ", %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))


def parse_response(response):
    # █▓▒░
    return {
        Response.NOT_FOUND: colorama.Back.RED + '4',
        Response.SKIPPED: colorama.Fore.GREEN + u'▓',
        Response.DOWNLOADED: colorama.Back.GREEN + ' ',
        Response.NOT_RECOGNIZED: colorama.Back.YELLOW + '?'
    }[response]


def download_rss(filename, urls_to_check=None):
    file, file_extension = os.path.splitext(filename)
    if urls_to_check is None:
        urls_to_check = [DOUBLE_URL, DEF_URL, TABLET_URL, IXB_URL]
        priority_path = {
            '.png': DOUBLE_URL,
            '.xml': DOUBLE_URL,
            '.text': DEF_URL,
            '.ogg': DEF_URL,
            '.rcss': TABLET_URL,
            '.rml': DEF_URL,
            '.ixb': IXB_URL
        }.get(file_extension, '')
        if priority_path == '':
            return (Response.NOT_RECOGNIZED, filename)

        # Prioritize specific URL
        urls_to_check.remove(priority_path)
        urls_to_check.insert(0, priority_path)
    else:
        pass #return (Response.NOT_RECOGNIZED, filename)

    # No more URLs to check, file wasn't found
    if len(urls_to_check) == 0:
        return (Response.NOT_FOUND, filename)
        
    # Get path to check
    path = urls_to_check.pop(0)
    
    try:
        if os.path.isfile('data/' + filename):
            return (Response.SKIPPED, filename)
        else:
            data = download(path + filename)
            write(data, 'data/' + filename)
            return (Response.DOWNLOADED, filename)
    except urllib2.HTTPError, err:
        if err.code == 404:
            # Try again on other URL
            #return (Response.NOT_FOUND, filename)
            return download_rss(filename, urls_to_check)
        else:
            raise


def download(filename, total_size=None, verbose=False):
    response = urllib2.urlopen(filename)
    if total_size is None:
        header = response.info().getheader('Content-Length')
        if header is None:
            total_size = None
        else:
            total_size = int(header.strip())
    bytes_so_far = 0
    chunks = ''

    while 1:
        chunk = response.read(8192)
        bytes_so_far += len(chunk)

        if not chunk:
            break

        if verbose:
            chunk_report(filename, bytes_so_far, total_size)

        chunks += chunk

    #sys.stdout.write("\n")
    return chunks

if __name__ == '__main__':
    if os.path.isfile(MANIFEST_FILE):
        data = read(MANIFEST_FILE)
    else:
        data = download(MANIFEST_URL, 5441013, verbose=True)
        print('')
        # save to cache
        write(data, MANIFEST_FILE)

    pool = Pool(processes=15)
    data = json.loads(data)
    if not os.path.exists('data'):
        os.makedirs('data')

    out = []

    for i in pool.imap_unordered(download_rss, data['files']):
        out.append(i)
        print (parse_response(i[0]), end = colorama.Style.RESET_ALL)
    
    not_found = [x for x in out if x[0] == Response.NOT_FOUND]
    print("\nNot found:\n" + "\n".join([x[1] for x in not_found]))
    print(str(len(not_found)) + ' / ' + str(len(data['files'])))
