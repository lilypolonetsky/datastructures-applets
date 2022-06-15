__doc__ = """ 
Program to show data structure visualizations in a tabbed Tk notebook
presentation form.  This program loads all the visualization modules
in the current directory that contain subclasses of VisualizationApp.
It and instantiates each one in a separate tab.  When the user clicks
on a tab, it calls the class's runVisualization method.  A preferred
order for the modules (by class name) controls the order of the
recognized modules.  The rest are added in alphabetical order. 
"""

import argparse, sys, os, random
from importlib import *
from tkinter import ttk

try:
    from allVisualizationsCommon import *
    import VisualizationApp
    VAP = VisualizationApp.VisualizationApp
    from tkUtilities import *
except ModuleNotFoundError:
    from .allVisualizationsCommon import *
    from .VisualizationApp import VisualizationApp as VAP
    from .tkUtilities import *

PREFERRED_ARRANGEMENT = [
    ['Chapters 1-4',
     ['Array', 'OrderedArray', 'SimpleArraySort', 'Stack', 'Queue',
      'PriorityQueue', 'InfixCalculator']],
    ['Chapters 5-7',
     ['LinkedList', 'OrderedList', 'TowerOfHanoi', 'Mergesort',
      'AdvancedArraySort']],
    ['Chapters 8-11',
     ['BinaryTree','Tree234', 'AVLTree', 'RedBlackTree',
      'HashTableOpenAddressing', 'HashTableChaining']],
    ['Chapters 12-16',
     ['PointQuadtree', 'Heap', 'Graph', 'WeightedGraph', 'BloomFilter',
      'SkipList']],
    ]
    
TAB_FONT = ('Calibri', -16)
INTRO_FONT = ('Helvetica', -16)

desktopInstructions = '''
Select a chapter and a visualization from the tabs at the top to see the
different data structures.
'''

trinketInstructions = '''
Select a chapter and a visualization from the tabs at the top to see the
different data structures.  If you are viewing this in a browser on a
touch screen device, you may not be allowed to tap on text entry boxes
and use the soft keyboard to enter values.
'''

def showVisualizations(   # Display a set of VisualizationApps in a ttk.Notebook
        classes, start=None, title="Datastructure Visualizations", 
        adjustForTrinket=False, seed='3.14159', verbose=0, debug=False,
        theme='alt', introBG='white'):
    if len(classes) == 0:
        print('No matching classes to visualize', file=sys.stderr)
        return
    if seed and len(seed) > 0:
        random.seed(seed)
    top = Tk()
    ttkStyle = ttk.Style()
    if theme:
        if debug:
            print('Starting theme:', ttkStyle.theme_use(), 'among',
                  ttkStyle.theme_names())
        ttkStyle.theme_use(theme)
        if debug:
            print('Set theme to', ttkStyle.theme_use())    
    top.title(title)

    padBy = abs(INTRO_FONT[1]) * 3
    labelStyleName='Intro.TLabel'
    top['bg'] = introBG
    frameStyleName='Intro.TFrame'
    ttkStyle.configure(frameStyleName, bg=introBG)
    notebook = ttk.Notebook(top)
    notebookStyle = ttk.Style(notebook)
    intro = Frame(top, padx=padBy, pady=padBy, bg=introBG)
    introCenter = Frame(intro, bg=introBG)
    nextline = makeIntro(
        intro_msg.format(
            customInstructions=(trinketInstructions if adjustForTrinket else 
                                desktopInstructions).strip()),
        introCenter, styleName=labelStyleName, bg=introBG,
        URLfg=None if adjustForTrinket else 'blue',
        URLfont=None if adjustForTrinket else INTRO_FONT + ('underline',) )
    loading = ttk.Label(introCenter, text='\nLoading ...', 
                        font=INTRO_FONT + ('italic',), style=labelStyleName)
    loading.grid(row=nextline, column=0)
    introCenter.grid(row=0, column=0)
    notebook.add(intro, state=NORMAL, text='Introduction')
    intro.bind('<Map>', mapHandler(introCenter, padBy, debug=debug), '+')
    if debug:
        fields = set(('width', 'height'))
        intro.bind('<Configure>', genericEventHandler(fields=fields), '+')
    notebook.pack(expand=True, fill=BOTH)
    
    # Waiting here for notebook visibility sometimes hangs
    # notebook.wait_visibility(top)  
               
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
                vizApp.DEBUG = debug
                name = getattr(vizApp, 'title', app.__name__)
                pane.bind('<Map>', oneTimeShowHintHandler(vizApp), '+')

            except Exception as e:
                name = app.__name__
                msg = 'Error instantiating {}:\n{}'.format(name, e)
                label = Label(pane, text=msg, fg='red')
                label.pack()
                print(msg, file=sys.stderr)
                
            group.add(pane, text=name)
            if start and start.lower() in (app.__name__.lower(), name.lower()):
                notebook.select(group)
                group.select(pane)
    loading.destroy()
    resizeIntro(intro, padBy)
    top.mainloop()

def mapHandler(introCenter, padding, debug=False):
    def mHandler(event):
        intro = event.widget
        if debug:
            x, y, width, height = intro.grid_bbox(column=0, row=0)
            print('Map event on', event.widget,
                  'current width =', event.widget.winfo_width())
            print('Intro widget size =', intro.winfo_width(), 'x',
                  intro.winfo_height(),
                  '\ncolumn 0 configuration =', intro.columnconfigure(0))
            print('IntroCenter size =', introCenter.winfo_width(), 'x',
                  introCenter.winfo_height())
            print('Intro padding', padding)
            print('Grid (0, 0) starts at', (x, y), 'with size', (width, height))
        resizeIntro(intro, padding)
    return mHandler

def resizeIntro(intro, padding):
    intro.columnconfigure(0, minsize=intro.winfo_width() - padding * 2)
    intro.rowconfigure(0, minsize=intro.winfo_height() - padding * 2)

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
        '-t', '--title',  default='Datastructure Visualizations',
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
        '-d', '--debug', default=False, action='store_true',
        help='Show debugging information.')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Add verbose comments')
    args = parser.parse_args()

    if args.files is None or args.files == []:
        dirs = set([os.path.relpath(os.getcwd())])
        if (sys.argv and os.path.exists(sys.argv[0]) and
            os.path.dirname(sys.argv[0])):
            dirs.add(os.path.dirname(sys.argv[0]))
        try:
            if os.path.exists(__file__) and os.path.dirname(__file__):
                dirs.add(os.path.dirname(__file__))
        except:
            pass
        if args.verbose > 1:
            print('No files provided.  Unique directories to search:', dirs,
                  'with search order:', list(dirs))
        args.files = list(dirs)
    showVisualizations(findVisualizations(args.files, args.verbose),
                       start=args.start, title=args.title, verbose=args.verbose,
                       adjustForTrinket=args.warn_for_trinket, debug=args.debug,
                       seed=args.seed)
