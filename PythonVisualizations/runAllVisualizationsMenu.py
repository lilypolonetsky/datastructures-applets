#! /usr/bin/env python3
__doc__ = """
Program to show algorithm visualizations one at at time with a
dropdown menu to select one.  This program loads all the visualization
modules in the current directory that contain subclasses of
VisualizationApp.  It instantiates each one in a separate Frame, and
builds a menu to choose one.  When the user selects a visualization,
the frame is shown (by using grid to manage its geometry) and all the
others are hidden.  A preferred order for the modules (by class or
name) controls the order of the recognized modules and groups them
with a prefix 'folder' name.  The rest are added in alphabetical
order in a folder called 'Other'.
"""

import argparse, sys, re, webbrowser, os, glob, random
from importlib import *
from tkinter import *
from tkinter import ttk

try:
    import VisualizationApp
    VAP = VisualizationApp.VisualizationApp
except ModuleNotFoundError:
    from .VisualizationApp import VisualizationApp as VAP

PREFERRED_ARRANGEMENT = [
    ['Chapter 2', ['Array', 'OrderedArray']],
    ['Chapter 3', ['SimpleArraySort']],
    ['Chapter 4', ['Stack', 'Queue', 'PriorityQueue', 'InfixCalculator']],
    ['Chapter 5', ['LinkedList', 'OrderedList']],
    ['Chapter 6', [ 'TowerOfHanoi', 'Mergesort']],
    ['Chapter 7', ['AdvancedArraySort']],
    ['Chapter 8', ['BinaryTree']],
    ['Chapter 9', ['Tree234']],
    ['Chapter 10', ['AVLTree', 'RedBlackTree']],
    ['Chapter 11', ['Quadtree']],
    ['Chapter 12', ['HashTableOpenAddressing', 'HashTableChaining']],
    ['Chapter 13', ['Heap']],
    ['Chapter 14', ['Graph']],
    ['Chapter 15', ['WeightedGraph']],
    ['Chapter 16', ['BloomFilter', 'SkipList']],
    ]

pathsep = re.compile(r'[/\\]')

def findVisualizations(filesAndDirectories, verbose=0):
    classes = set()
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
                         if isStringInFile('runVisualization()', f)]:
            dirs = pathsep.split(os.path.normpath(os.path.dirname(filename)))
            if dirs and dirs[0] == '.':
                dirs.pop(0)
            modulename, ext = os.path.splitext(os.path.basename(filename))
            if modulename:
                try:
                    fullmodulename = '.'.join(dirs + [modulename])
                    if verbose > 1:
                        print('Attempting to import {} ... ' .format(
                            fullmodulename), file=sys.stderr, end='')
                    module = import_module(fullmodulename)
                    if verbose > 1:
                        print('Imported. Looking for VisualizationApp'
                              .format(fullmodulename),
                              file=sys.stderr)
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
    return classes
    
def isStringInFile(text, filename):
    with open(filename, 'r') as f:
        return text in f.read()
            
def findVisualizationClasses(module, verbose=0):
    classes = []
    for name in dir(module):
        this = getattr(module, name)          # Check if this 
        if (isinstance(this, type(object)) and # is a class
            issubclass(this, VAP) and this is not VAP and # a subclass of VAP
            this.__module__ == module.__name__): # defined in ths module
            classes.append(this)
        elif verbose > 2:
            print('Ignoring {}.{} of type {}'.format(
                module.__name__, name, type(this)), file=sys.stderr)
    return classes

URL_pattern = re.compile(r'(https*|ftp)://[\w-]+\.[\w/.,?&=#%-]+')

INTRO_FONT = ('Helvetica', -16)
MENU_FONT = ('Helvetica', -12)

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
Select a visualization from the menu at the top to see the
different data structures.  Place cursor near top edge to restore
visualization selection menu.  Resizing the window does not alter
the visualization.
'''

trinketInstructions = '''
Select a visualization from the menu at the top to see the
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

appWindows = []
userSelectedWindow = None
chosenStyle = ('bold',)

def raiseAppWindowHandler(appWindow, menubutton, menu, adjustForTrinket=False):
    def handler():
        global userSelectedWindow
        appWindow.grid(row=1, column=0)
        userSelectedWindow = appWindow
        for i, a in enumerate(appWindows):
            if a.winfo_ismapped() and a is not appWindow:
                a.grid_remove()
            menu.entryconfigure(
                i, font=MENU_FONT + (chosenStyle if a is appWindow else ()))
        if appWindow != appWindows[0] and not adjustForTrinket:
            menubutton.grid_remove()
    return handler

# Collapsible menubar remains visible to indicate where user can hover
# pointer to restore the menu
MIN_MENUBAR_HEIGHT = 2
HOVER_DELAY = 500        # Milliseconds to wait before showing menu

def makeArmMenuHandler(menubar, menu):
    def handler(event):
        setattr(
            menubar, 'timeout_ID',
            menubar.after(
                HOVER_DELAY, 
                lambda: menu.grid() or setattr(menubar, 'timeout_ID', None)))
    return handler

def makeDisarmMenuHandler(menubar, menu):
    def handler(event):
        if event.widget == menubar and getattr(menubar, 'timeout_ID'):
            menubar.after_cancel(getattr(menubar, 'timeout_ID'))
        setattr(menubar, 'timeout_ID', None)
    return handler

def resizeHandler(event):
    if event.widget in appWindows:
        print('Resize of application window', event.widget, 'to',
              event.widget.winfo_width(), 'x', event.widget.winfo_height())

def genericEventHandler(event):
    if event.widget in appWindows:
        appTitle = getattr(event.widget, 'appTitle', '')
        if appTitle: appTitle += ' '
        print('{} event on {}application window {}'.format(
            event.type, appTitle, event.widget))
        
def showVisualizations(   # Display a set of VisualizationApps in a ttk.Notebook
        classes, start=None, title="Algorithm Visualizations", 
        adjustForTrinket=False, seed='3.14159', verbose=0):
    if len(classes) == 0:
        print('No matching classes to visualize', file=sys.stderr)
        return
    if seed and len(seed) > 0:
        random.seed(seed)
    top = Tk()
    top.title(title)
    ttk.Style().configure(
        'TFrame', bg=getattr(VAP, 'DEFAULT_BG', 'white'))

    if adjustForTrinket:
        VAP.MIN_CODE_CHARACTER_HEIGHT = 9
    restoreMenu = Canvas(top, height=MIN_MENUBAR_HEIGHT, bg='pink')
    restoreMenu.grid(row=0, column=0, sticky=(E, W, N, S))
    menubutton = Menubutton(top, text='Select Visualization',
                            font=MENU_FONT)
    menubutton.grid(row=0, column=0)
    restoreMenu.bind('<Enter>', makeArmMenuHandler(restoreMenu, menubutton))
    restoreMenu.bind('<Leave>', makeDisarmMenuHandler(restoreMenu, menubutton))
    
    intro = ttk.Frame(top, padding=abs(INTRO_FONT[1])*3)
    nextline = makeIntro(
        intro_msg.format(
            customInstructions=(trinketInstructions if adjustForTrinket else 
                                desktopInstructions).strip()),
        intro, URLfg=None if adjustForTrinket else 'blue',
        URLfont=None if adjustForTrinket else INTRO_FONT + ('underline',) )
    loading = ttk.Label(intro, text='\nLoading ...', 
                        font=INTRO_FONT + ('italic',))
    loading.grid(row=nextline, column=0)
    appWindows.append(intro)
    intro.grid(row=1, column=0)
    top.rowconfigure(1, minsize=600)
    top.columnconfigure(0, minsize=VAP.DEFAULT_CANVAS_WIDTH)
    # top.bind('<Configure>', resizeHandler)
    
    menu = Menu(menubutton, tearoff=0)
    menu.add_command(label='Introduction', 
                     command=raiseAppWindowHandler(intro, menubutton, menu,
                                                   adjustForTrinket),
                     font=MENU_FONT + chosenStyle)
    menubutton['menu'] = menu

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

    startAppWindow = None
    for folder in folders:
        if folders[folder]:
            if verbose > 0:
                print('Constructing folder {}'.format(folder), file=sys.stderr)
        for app in folders[folder]:
            if verbose > 0:
                print('Found app {} and instantiating in {}'.format(
                    app.__name__, folder),
                      file=sys.stderr)
            pane = ttk.Frame(top)
            loading['text'] = '\nLoading module {} of {} modules...'.format(
                len(appWindows), len(classes))
            appWindows.append(pane)
            try:
                vizApp = app(window=pane)
                appTitle = getattr(vizApp, 'title', app.__name__)
                name = folder + ': ' + appTitle
                setattr(pane, 'appTitle', appTitle)
                if verbose > 0:
                    for eventType in ('<Map>', '<Visibility>'):
                        pane.bind(eventType, genericEventHandler, '+')
            except Exception as e:
                name = app.__name__ + ' *'
                msg = 'Error instantiating {}:\n{}'.format(app.__name__, e)
                label = Label(pane, text=msg, fg='red')
                label.grid()
                print(msg, file=sys.stderr)

            if start and start.lower() in (
                    getattr(vizApp, 'title', app.__name__).lower(),
                    app.__name__.lower()):
               startAppWindow = pane
               
               pane.grid(row=1, column=0, sticky=(N, E, W, S))
               menu.entryconfigure(0, font=MENU_FONT)
               
            menu.add_command(
                label=name, 
                font=MENU_FONT + (
                    chosenStyle if startAppWindow == pane else ()),
                command=raiseAppWindowHandler(pane, menubutton, menu,
                                              adjustForTrinket))

    for i, appWindow in enumerate(appWindows[1:]):
        if (appWindow is not (userSelectedWindow or startAppWindow) and
            appWindow.winfo_ismapped()):
            appWindow.grid_remove()

    loading.destroy()
    if verbose > 1:
        print('Top geometry:', top.winfo_geometry(),
              'Menubutton geometry:', menubutton.winfo_geometry(),
              'RestoreMenu geometry:', restoreMenu.winfo_geometry(),
              'RestoreMenu height:', restoreMenu['height'],
              file=sys.stderr)
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
        help='Starting visualization.  '
        'Should match one of the visualization module titles or class name.')
    parser.add_argument(
        '-t', '--title',  default='Algorithm Visualizations',
        help='Title for top level window')
    parser.add_argument(
        '-w', '--warn-for-trinket', default=False, action='store_true',
        help='Adjust settings and warn users about limitations of use on '
        'Trinket.io')
    parser.add_argument(
        '--seed', default='3.14159',
        help='Random number generator seed.  Set to empty string to skip '
        'seeding.')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Add verbose comments')
    args = parser.parse_args()
        
    if args.files is None or args.files == []:
        args.files = [os.path.dirname(sys.argv[0]) or
                      os.path.relpath(os.getcwd())]
    showVisualizations(findVisualizations(args.files, args.verbose),
                       start=args.start, title=args.title, verbose=args.verbose,
                       adjustForTrinket=args.warn_for_trinket,
                       seed=args.seed)
