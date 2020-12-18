#! /usr/bin/env python3
__doc__ = """ 
Program to show algorithm visualizations in a tabbed Tk notebook
presentation form.  This program loads all the visualization modules
in the current directory that contain subclasses of VisualizationApp.
It and instantiates each one in a separate tab.  When the user clicks
on a tab, it calls the class's runVisualization method.  A preferred
order for the modules (by class name) controls the order of the
recognized modules.  The rest are added in alphabetical order. 
"""

import argparse, sys, re, webbrowser, os, glob
from importlib import *
from tkinter import *
from tkinter import ttk

try:
    from VisualizationApp import *
except ModuleNotFoundError:
    from .VisualizationApp import *

PREFERRED_ARRANGEMENT = [
    ['Chapters 1-4',
     ['Array', 'OrderedArray', 'SimpleArraySort', 'Stack', 'Queue',
      'PriorityQueue', 'InfixCalculator']],
    ['Chapters 5-7',
     ['LinkedList', 'OrderedList', 'TowerOfHanoi', 'MergeSort',
      'AdvancedArraySort']],
    ['Chapters 8-11',
     ['BinaryTree','Tree234', 'AVLTree', 'RedBlackTree', 'Quadtree']],
    ['Chapters 12-16',
     ['HashTableOpenAddressing', 'HashTableChaining', 'Heap', 
      'Graph', 'WeightedGraph', 'BloomFilter', 'SkipList']],
    ]

pathsep = re.compile(r'[/\\]')

def findVisualizations(filesAndDirectories, verbose=0):
    classes = set()
    for fileOrDir in filesAndDirectories:
        isDir = os.path.isdir(fileOrDir)
        if verbose > 1:
            print('Looking for "runVisualization()" in',
                  'python files in {}'.format(fileOrDir) if isDir else isDir,
                  file=sys.stderr)
        files = glob.glob(os.path.join(fileOrDir, '*.py')) if isDir else [
                   fileOrDir]
        for filename in [f for f in files 
                         if isStringInFile('runVisualization()', f)]:
            dirs = pathsep.split(os.path.normpath(os.path.dirname(filename)))
            if dirs and dirs[0] == '.':
                dirs.pop(0)
            modulename, ext = os.path.splitext(os.path.basename(filename))
            if modulename:
                try:
                    fullmodulename = '.'.join(dirs + [modulename])
                    module = import_module(fullmodulename)
                    if verbose > 1:
                        print('Imported {} and looking for VisualizationApp'
                              .format(fullmodulename),
                              file=sys.stderr)
                    classes |= set(findVisualizationClasses(
                        module, verbose=verbose))
                except ModuleNotFoundError:
                    if verbose > 1:
                        print('Unable to import module', modulename,
                              file=sys.stderr)
    return classes
    
def isStringInFile(text, filename):
    with open(filename, 'r') as f:
        return text in f.read()
            
def findVisualizationClasses(module, verbose=0):
    classes = []
    for name in dir(module):
        this = getattr(module, name)
        if isinstance(this, type(VisualizationApp)) and (
                hasattr(this, 'runVisualization') and
                len(this.__subclasses__()) == 0 and
                this is not VisualizationApp):
            if verbose > 1:
                print('Found {}.{}, a subclass of VisualizationApp'.format(
                    module.__name__, name))
            classes.append(this)
        elif verbose > 2:
            print('Ignoring {}.{} of type {}'.format(
                module.__name__, name, type(this)), file=sys.stderr)
    return classes

URL_pattern = re.compile(r'(https*|ftp)://[\w-]+\.[\w/.,?&=#%-]+')

TAB_FONT = ('Calibri', -16)
INTRO_FONT = ('Helvetica', -16)

intro_msg = """
Welcome to the algorithm visualizations for the book:
Data Structures and Algorithms in Python

Please use these visualization tools along with the book to improve
your understanding of how computers organize and manipulate data
efficiently.

{customInstructions}

Exceptional students in the Computer Science Department of
Stern College at Yeshiva University developed these visualizations.
https://www.yu.edu/stern/ug/computer-science
"""

desktopInstructions = '''
Select a chapter and a visualization from the tabs at the top to see the
different data structures.
'''

trinketInstructions = '''
Select a chapter and a visualization from the tabs at the top to see the
different data structures.  If you are viewing this in a browser on a
touch screen device, you may not be allowed to click on text entry
boxes and use the soft keyboard to enter values.
'''

def openURL(URL):         # Make a callback function to open an URL
    return lambda e: webbrowser.open(URL)

def makeIntro(
        mesg, container, font=INTRO_FONT, URLfg='blue', 
        URLfont=INTRO_FONT + ('underline',), row=0, column=0):
    '''Make introduction screen as a sequence of labels for each line of a
    a message.  The labels are stacked, centered inside a container
    widget.  URLs are converted to a label within a frame that has a
    binding to open the URL.
    Increment row for each line added and return the grid row for the
    next row of the container.
    '''
    for line in mesg.split('\n'):
        URLs = ([m for m in URL_pattern.finditer(line)] if URLfg and URLfont 
                else [])
        if URLs:
            URLframe = ttk.Frame(container, cursor='hand2')
            last = 0
            col = 0
            for match in URLs:
                if match.start() > last:
                    label = ttk.Label(URLframe, text=line[last:match.start()],
                                      font=font)
                    label.grid(row=0, column=col)
                    col += 1
                link = ttk.Label(
                    URLframe, text=match.group(), font=URLfont,
                    foreground=URLfg)
                link.grid(row=0, column=col)
                col += 1
                link.bind('<Button-1>', openURL(match.group()))
                last = match.end()
            if last < len(line):
                label = ttk.Label(URLframe, text=line[last:], 
                                  font=font)
                label.grid(row=0, column=col)
                col += 1
            URLframe.grid(row=row, column=column)
        else:
            label = ttk.Label(container, text=line, font=font)
            label.grid(row=row, column=column)
        row += 1
    return row

def showVisualizations(   # Display a set of VisualizationApps in a ttk.Notebook
        classes, start=None, title="Algorithm Visualizations", 
        adjustForTrinket=False, verbose=0):
    if len(classes) == 0:
        print('No matching classes to visualize', file=sys.stderr)
        return
    top = Tk()
    top.title(title)
    notebook = ttk.Notebook(top)
    notebookStyle = ttk.Style(notebook)
    intro = ttk.Frame(notebook, padding=abs(INTRO_FONT[1])*3)
    nextline = makeIntro(
        intro_msg.format(
            customInstructions=(trinketInstructions if adjustForTrinket else 
                                desktopInstructions).strip()),
        intro, URLfg=None if adjustForTrinket else 'blue',
        URLfont=None if adjustForTrinket else INTRO_FONT + ('underline',) )
    loading = ttk.Label(intro, text='\nLoading ...', 
                        font=INTRO_FONT + ('italic',))
    loading.grid(row=nextline, column=0)
    notebook.add(intro, state=NORMAL, text='Introduction')
    notebook.pack(expand=True, fill=BOTH)
    notebook.wait_visibility(top)
               
    classes_dict = dict((app.__name__, app) for app in classes)
    ordered_classes = [
        classes_dict[app] for folder, apps in PREFERRED_ARRANGEMENT
        for app in apps if app in classes_dict]
    folders = {}
    for folder, apps in PREFERRED_ARRANGEMENT:
        folders[folder] = [
            classes_dict[app] for app in apps if app in classes_dict]
    otherApps = [app for app in classes
                 if not any(app.__name__ in apps for folder, apps in
                            PREFERRED_ARRANGEMENT)]
    if otherApps:
        folders['Other'] = otherApps
    ordered_classes += otherApps

    appNumber = 1
    for folder in folders:
        if folders[folder]:
            if verbose > 0:
                print('Constructing folder {}'.format(folder), file=sys.stderr)
            group = ttk.Notebook(notebook)
            notebook.add(group, text=folder)
        for app in folders[folder]:
            if verbose > 0:
                print('Found app {} and instantiating in {}'.format(
                    app.__name__, folder),
                      file=sys.stderr)
            pane = ttk.Frame(group)
            loading['text'] = '\nLoading module {} of {} modules...'.format(
                appNumber, len(classes))
            appNumber += 1
            try:
                vizApp = app(window=pane)
                name = getattr(vizApp, 'title', app.__name__)
            except Exception as e:
                name = app.__name__
                msg = 'Error instantiating {}:\n{}'.format(name, e)
                label = Label(pane, text=msg, fg='red')
                label.pack()
                print(msg, file=sys.stderr)
                
            group.add(pane, text=name)
            if start and start.lower() in (app.__name__.lower(), name.lower()):
                notebook.select(folder)
                group.select(pane)
    loading.destroy()
    nPadding = notebookStyle.configure('TNotebook').get('padding', [0] * 4)
    iPadding = intro.config('padding')[-1][0]
    iPadding = int(iPadding if isinstance(iPadding, str) else iPadding.string)
    intro.bind('<Configure>', 
               resizeIntro(intro, nPadding[0] + nPadding[2] + iPadding))
    top.mainloop()

def resizeIntro(intro, padding):
    def handler(event):
        # print('Widget', event.widget, 'width =', event.widget.winfo_width())
        # print('Intro widget width =', intro.winfo_width(),
        #       ' padding =', intro.config('padding')[-1], 
        #       ' column 0 configuration =', intro.columnconfigure(0))
        # print('Notebook padding', padding)
        newsize = intro.winfo_width() - padding
        # print('Desired column minsize', newsize)
        newsize = min(780, newsize)
        # print('Set column minsize to', newsize)
        intro.columnconfigure(0, minsize=newsize)
    return handler

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'files', metavar='FILE-or-DIR', nargs='*',
        help='File or directory containing VisualizationApp programs. ' 
        'The default is to search the directory where this Python program '
        'is stored.')
    parser.add_argument(
        '-s', '--start', 
        help='Starting visualization.  '
        'Should match one of the visualization module titles or class name.')
    parser.add_argument(
        '-t', '--title',  default='Algorithm Visualizations',
        help='Title for top level window')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Add verbose comments')
    args = parser.parse_args()

    if args.files is None or args.files == []:
        args.files = [os.path.dirname(sys.argv[0]) or
                      os.path.relpath(os.getcwd())]
    showVisualizations(findVisualizations(args.files, args.verbose),
                       start=args.start, title=args.title, verbose=args.verbose)
