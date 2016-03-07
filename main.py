from __future__ import print_function
import urllib2
import sys
import json
import os.path
import io


MANIFEST_URL = 'http://206drody.mobboss-online.com/index.php?action=manifest&app_version=0&controller=file&dpi=2x&lang=en&layout=tablet&opcode=op1'
IXB_PATH = 'http://cdn-aws.mobboss-online.com/5087/_ixb/'
PNG_PATH = 'http://cdn-aws.mobboss-online.com/5087/2x/'
XML_PATH = 'http://cdn-aws.mobboss-online.com/5087/2x/'
RCSS_PATH = 'http://cdn-aws.mobboss-online.com/5087/tablet/'
RML_PATH = 'http://cdn-aws.mobboss-online.com/5087/_def/'
TEXT_PATH = 'http://cdn-aws.mobboss-online.com/5087/_def/'
OGG_PATH = 'http://cdn-aws.mobboss-online.com/5087/_def/'
MANIFEST_FILE = 'manifest.json'


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


def download_rss(filename):
    file, file_extension = os.path.splitext(filename)
    path = {
        '.png': PNG_PATH,
        '.xml': XML_PATH,
        '.text': TEXT_PATH,
        '.ogg': OGG_PATH,
        '.rcss': RCSS_PATH,
        '.rml': RML_PATH,
        '.ixb': IXB_PATH
    }.get(file_extension, '')
    if path == '':
        print (filename + ' not recognized.')
    else:
        try:
            data = download(path + filename)
            write(data, 'data/' + filename)
        except urllib2.HTTPError, err:
            if err.code == 404:
                print (path + filename + ' not found')
            else:
                raise
    return ''


def download(filename, total_size=None):
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

        chunk_report(filename, bytes_so_far, total_size)

        chunks += chunk

    sys.stdout.write("\n")
    return chunks

if __name__ == '__main__':
    if os.path.isfile(MANIFEST_FILE):
        data = read(MANIFEST_FILE)
    else:
        data = download(MANIFEST_URL, 5441013)
        # save to cache
        write(data, MANIFEST_FILE)

    data = json.loads(data)
    if not os.path.exists('data'):
        os.makedirs('data')
    for url in data['files']:
        download_rss(url)
