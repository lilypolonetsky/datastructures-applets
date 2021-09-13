#! /usr/bin/env python3
__doc__ = """
Common components of the runAllVisualization tools.
"""

import sys, re, webbrowser, os, glob
from importlib import *
from tkinter import ttk

try:
    import VisualizationApp
    VAPs = (VisualizationApp.VisualizationApp,)
except ModuleNotFoundError:
    from .VisualizationApp import VisualizationApp as VAP
    VAPs = (VAP,)
    
pathsep = re.compile(r'[/\\]')
runVizCallPattern = re.compile(
    r'\n[^#]*\.runVisualization\(\)(?!.*#\s*runAllVisualizations ignore)')

def findVisualizations(filesAndDirectories, verbose=0):
    global VAPs
    classes = set()
    try:
        orig__path__ = sys.path
    except NameError:
        orig__path__ = None
        sys.path = []
    for fileOrDir in filesAndDirectories:
        isDir = os.path.isdir(fileOrDir)
        files = glob.glob(os.path.join(fileOrDir, '*.py')) if isDir else [
                   fileOrDir]
        if verbose > 1:
            print(
                'Looking for "runVisualization()" in',
                '{} python files in {}'.format(len(files), fileOrDir) if isDir
                else fileOrDir,
                file=sys.stderr)
            if verbose > 2 and isDir:
                print('Files:', '\n'.join(files), file=sys.stderr)
        for filename in [f for f in files 
                         if isPatternInFile(runVizCallPattern, f)]:
            dirs = pathsep.split(os.path.normpath(os.path.dirname(filename)))
            if dirs and dirs[0] == '.':
                dirs.pop(0)
            modulename, ext = os.path.splitext(os.path.basename(filename))
            if modulename:
                try:
                    path = '/'.join(dirs)
                    addPath = path and not path in sys.path
                    if verbose > 1:
                        if addPath:
                            print('Adding {} to sys.path ...'.format(path),
                                  file=sys.stderr)
                        print('Attempting to import {} ... ' .format(
                            modulename), file=sys.stderr, end='')
                    if addPath:
                        sys.path.append(path)
                        try:
                            vap = import_module('VisualizationApp')
                            if not vap in VAPs:
                                VAPs = (vap.VisualizationApp, *VAPs)
                        except ModuleNotFoundError:
                            pass
                    module = import_module(modulename)
                    if verbose > 1:
                        print('Imported. Looking for VisualizationApp'
                              .format(modulename), file=sys.stderr)
                    newclasses = findVisualizationClasses(module, verbose)
                    if verbose > 1:
                        print('Found {} matching classes: {}'
                              .format(len(newclasses), newclasses),
                              file=sys.stderr)
                        previouslyFound = set(newclasses) & classes
                        if len(previouslyFound) > 0:
                            print('Previously found:', previouslyFound,
                                  file=sys.stderr)
                    classes |= set(newclasses)
                except ModuleNotFoundError:
                    if verbose > 0:
                        print('Unable to import module', modulename,
                              file=sys.stderr)
    if orig__path__ is not None:
        sys.path = orig__path__
    return classes

def isPatternInFile(textOrRegex, filename):
    with open(filename, 'r') as f:
        return (text in f.read()) if isinstance(textOrRegex, str) else (
            textOrRegex.search(f.read())
            if isinstance(textOrRegex, type(pathsep)) else False)

def findVisualizationClasses(module, verbose=0):
    classes = []
    for name in dir(module):
        this = getattr(module, name)          # Check if this 
        if (isinstance(this, type(object)) and # is a class that is a proper
            issubclass(this, VAPs) and not (this in VAPs) and # subclass of VAP
            this.__module__ == module.__name__): # defined in ths module
            classes.append(this)
        elif verbose > 2:
            print('Ignoring {}.{} of type {}'.format(
                module.__name__, name, type(this)), file=sys.stderr)
    return classes

URL_pattern = re.compile(r'(https*|ftp)://[\w-]+\.[\w/.,?&=#%-]+')

intro_msg = """
Welcome to the algorithm visualizations for the book:
Data Structures and Algorithms in Python

Please use these visualization tools along with the book to improve your
understanding of how computers organize and manipulate data efficiently.

{customInstructions}

Exceptional students in the Computer Science Department of Stern College
for Women at Yeshiva University helped develop these visualizations.
https://www.yu.edu/stern/ug/computer-science
"""

def openURL(URL):         # Make a callback function to open an URL
    return lambda e: webbrowser.open(URL)

INTRO_FONT = ('Helvetica', -16)

def makeIntro(
        mesg, container, font=INTRO_FONT, URLfg='blue', bg='white',
        URLfont=INTRO_FONT + ('underline',), row=0, column=0,
        styleName='Intro.TLabel'):
    '''Make introduction screen as a sequence of labels for each line of a
    a message.  The labels are stacked, centered inside a container
    widget.  URLs are converted to a label within a frame that has a
    binding to open the URL.
    Increment row for each line added and return the grid row for the
    next row of the container.
    '''
    
    ttkStyle = ttk.Style(container)
    ttkStyle.configure(styleName, background=bg)
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
                                      font=font, style=styleName)
                    label.grid(row=0, column=col)
                    col += 1
                link = ttk.Label(
                    URLframe, text=match.group(), font=URLfont,
                    foreground=URLfg, style=styleName)
                link.grid(row=0, column=col)
                col += 1
                link.bind('<Button-1>', openURL(match.group()))
                last = match.end()
            if last < len(line):
                label = ttk.Label(URLframe, text=line[last:], font=font,
                                  style=styleName)
                label.grid(row=0, column=col)
                col += 1
            URLframe.grid(row=row, column=column)
        else:
            label = ttk.Label(container, text=line, font=font, style=styleName)
            label.grid(row=row, column=column)
        row += 1
    return row

def oneTimeShowHintHandler(visualizationApp, hintText=None, delay=500):
    'Creates an event handler to set the application hint after a delay'
    return lambda event: (
        getattr(visualizationApp, 'initial_hint_shown', False) or
        visualizationApp.window.after(
            delay, lambda: visualizationApp.setHint(visualizationApp.textEntries[0], hintText)) and
        setattr(visualizationApp, 'initial_hint_shown', True))
        
