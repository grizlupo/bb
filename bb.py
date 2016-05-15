import sys
import os
from PyPDF2 import PdfFileMerger
from tokenize import *

__version__ = '0.1.0'

def bookmark(filename, isdouble=False, strict=True):
    name, ext = os.path.splitext(filename)
    if ext.lower() == '.pdf':
        filename = name
    
    merger = PdfFileMerger(strict=strict)
    merger.append(open(filename + '.pdf', 'rb'), import_bookmarks=False)
    
    toc = open(filename + '.toc', 'rb')
    g = tokenize(toc.readline)
    encoding = next(g)[1]
    
    base = 0
    title = page = None
    parents = []
    recent = None
    parent = None
    minus = False
    lineno = 0
    for toknum, tokval, _, _, _ in g:
        #print(toknum, tok_name[toknum], tokval)
        if toknum == INDENT:
            parents.append(parent)
            parent = recent
        elif toknum == DEDENT:
            parent = parents.pop()
        elif toknum == STRING:
            title = eval(tokval)
        elif toknum == OP:
            if tokval == '-':
                minus = True
        elif toknum == NUMBER:
            page = int(tokval)
            if minus:
                page = -page
            minus = False
        elif toknum == NEWLINE:
            lineno += 1
            #print(title, base, page)
            if title:
                if not page:
                    print('expect page number at {} line: {!r}'.format(lineno, title), file=sys.stderr)
                    page = 1
                if isdouble:
                    # 문서의 두 페이지가 PDF의 한 페이지인 경우
                    pdf_page = base + (page - 1) // 2
                else:
                    pdf_page = base + (page - 1)
                recent = merger.addBookmark(title, pdf_page, parent)
            elif page:
                base = page - 1
            title = page = None
            
    outfile = open(filename + '_toc.pdf', 'wb')
    merger.write(outfile)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='build bookmark v{}'.format(__version__))
    parser.add_argument('pdf',
            help='pdf file name')
    parser.add_argument('-d', '--double', action='store_const',
            const=True, default=False,
            help='real two pages in pdf one page')
    parser.add_argument('--strict', action='store_true', default=True,
            help='process pdf in strict mode')
    parser.add_argument('--nostrict', dest='strict', action='store_false')

    args = parser.parse_args()
    print(args)
    if args.pdf:
        print('build', args.pdf, 'bookmark edition')
        bookmark(args.pdf, args.double, args.strict)
        
        
if __name__ == '__main__':
    main()
    
