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

import argparse, sys, re, webbrowser, os, subprocess, glob
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
     ['LinkedList', 'TowerOfHanoi', 'MergeSort', 'AdvancedArraySort']],
    ['Chapters 8-11',
     ['BinaryTree','Tree234', 'AVLTree', 'RedBlackTree', 'Quadtree']],
    ['Chapters 12-16',
     ['HashTableOpenAddressing', 'HashTableChaining', 'Heap', 
      'Graph', 'WeightedGraph', 'BloomFilter', 'SkipList']],
    ]

def findVisualizations(filesAndDirectories, verbose=0):
    classes = set()
    for fileOrDir in filesAndDirectories:
        isDir = os.path.isdir(fileOrDir)
        if verbose > 1:
            print('Looking for "runVisualization()" in',
                  'python files in {}'.format(fileOrDir) if isDir else isDir,
                  file=sys.stderr)
        cmd = ['fgrep', '-sl', 'runVisualization()'] + (
               glob.glob(os.path.join(fileOrDir, '*.py')) if isDir else [
                   fileOrDir])
        out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()
        for filename in out.decode().split('\n'):
            modulename, ext = os.path.splitext(os.path.basename(filename))
            if modulename:
                try:
                    module = __import__(modulename, globals(), locals(), [], 0)
                    classes |= set(findVisualizationClasses(
                        module, verbose=verbose))
                except ModuleNotFoundError:
                    if verbose > 1:
                        print('Unable to import module', modulename,
                              file=sys.stderr)
    return classes
            
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

Please use these visualization tools along with the
book to improve your understanding of how computers
organize and manipulate data efficiently.

Select tabs at the top to see the different data structures.


Exceptional students in the Computer Science Department of
Stern College at Yeshiva University developed these visualizations.
https://www.yu.edu/stern/ug/computer-science
"""

def openURL(URL):         # Make a callback function to open an URL
    return lambda e: webbrowser.open(URL)

def showVisualizations(   # Display a set of VisualizationApps in a ttk.Notebook
        classes, start=None, title="Algorithm Visualizations", verbose=0):
    if len(classes) == 0:
        print('No matching classes to visualize', file=sys.stderr)
        return
    top = Tk()
    top.title(title)
    ttk.Style().configure("TNotebook.Tab", font=TAB_FONT,
                          padding=[12, abs(TAB_FONT[1]) * 5 // 8, 12, 2])
    ttk.Style().configure(
        'TFrame', bg=getattr(VisualizationApp, 'DEFAULT_BG', 'white'))

    notebook = ttk.Notebook(top)
    intro = ttk.Frame(notebook)
    for line in intro_msg.split('\n'):
        URLs = [m for m in URL_pattern.finditer(line)]
        if URLs:
            frame = ttk.Frame(intro)
            last = 0
            for match in URLs:
                if match.start() > last:
                    ttk.Label(frame, text=line[last:match.start()],
                              font=INTRO_FONT).pack(side=LEFT)
                link = ttk.Label(
                    frame, text=match.group(), font=INTRO_FONT + ('underline',),
                    foreground="blue")
                link.pack(side=LEFT)
                link.bind('<Button-1>', openURL(match.group()))
                last = match.end()
            if last < len(line):
                ttk.Label(frame, text=line[last:], 
                          font=INTRO_FONT).pack(side=LEFT)
            frame.pack()
        else:
            ttk.Label(intro, text=line, font=INTRO_FONT).pack()
    loading = ttk.Label(intro, text='\nLoading ...', 
                        font=INTRO_FONT + ('italic',))
    loading.pack()
    notebook.add(intro, state=NORMAL, text='Introduction', padding=8)
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
    top.mainloop()

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
        help='Starting tab.  '
        'Should match one of the visualization module titles or class name.')
    parser.add_argument(
        '-t', '--title',  default='Algorithm Visualizations',
        help='Title for top level window')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Add verbose comments')
    args = parser.parse_args()

    if args.files is None or args.files == []:
        args.files = [os.path.dirname(sys.argv[0]) or os.getcwd()]
    showVisualizations(findVisualizations(args.files, args.verbose),
                       start=args.start, title=args.title, verbose=args.verbose)
