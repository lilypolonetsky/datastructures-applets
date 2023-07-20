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

import argparse, sys, os, random
from importlib import *
from tkinter import *
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
    ['Chapter 2', ['Array', 'OrderedArray']],
    ['Chapter 3', ['SimpleArraySort']],
    ['Chapter 4', ['Stack', 'Queue', 'PriorityQueue', 'InfixCalculator']],
    ['Chapter 5', ['LinkedList', 'OrderedList']],
    ['Chapter 6', [ 'TowerOfHanoi', 'Mergesort']],
    ['Chapter 7', ['AdvancedArraySort']],
    ['Chapter 8', ['BinaryTree']],
    ['Chapter 9', ['Tree234']],
    ['Chapter 10', ['AVLTree', 'RedBlackTree']],
    ['Chapter 11', ['HashTableOpenAddressing', 'HashTableChaining']],
    ['Chapter 12', ['PointQuadtree']],
    ['Chapter 13', ['Heap']],
    ['Chapter 14', ['Graph']],
    ['Chapter 15', ['WeightedGraph']],
    ['Chapter 16', ['BloomFilter', 'SkipList']],
    ]

INTRO_FONT = ('Helvetica', -16)
MENU_FONT = ('Helvetica', -12)

desktopInstructions = '''
Select a visualization from the menu at the top to see the different
data structures.  Place cursor near top edge to restore the
visualization selection menu.
'''

trinketInstructions = '''
Select a visualization from the menu at the top to see the different
data structures.  Place cursor near top edge to restore the visualization
selection menu.  If you are viewing this on a touch screen device, you may
not be allowed to tap on text entry boxes and use the soft keyboard to
enter values.
'''

DEBUG = False
appWindows = []
userSelectedWindow = None
chosenStyle = ('bold',)

def raiseAppWindowHandler(appWindow, menubutton, menu, adjustForTrinket=False,
                          sticky=(N, E, W, S)):
    def handler():
        global userSelectedWindow
        appWindow.grid(row=1, column=0, sticky=sticky)
        userSelectedWindow = appWindow
        for i, a in enumerate(appWindows):
            if a.winfo_ismapped() and a is not appWindow:
                a.grid_remove()
            menu.entryconfigure(
                i, font=MENU_FONT + (chosenStyle if a is appWindow else ()))
        if appWindow != appWindows[0]: # and not adjustForTrinket:
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
    vizApp = event.widget in appWindows
    width, height = event.widget.winfo_width(), event.widget.winfo_height()
    if vizApp:
        kind = 'appplication window ' + getattr(event.widget, 'appTitle')
    else:
        kind = 'top' if isinstance(event.widget, Tk) else 'internal'
    if DEBUG and (kind == 'top' or vizApp):
        print('Resize of', kind, event.widget, 'from', width, 'x', height, 'to',
              event.width, 'x', event.height)
    if kind == 'top' and event.width > 1 and event.height > 1:
        topPartHeight = 0
        for w in event.widget.grid_slaves(row=0, column=0):
            topPartHeight = max(topPartHeight, w.winfo_height())
        if DEBUG:
            print('Scheduling resize of window leaving', topPartHeight,
                  'at top')
        event.widget.after(
            50, lambda:
            event.widget.columnconfigure(0, minsize=event.width) or
            event.widget.rowconfigure(1, minsize=event.height - topPartHeight))
        
def showVisualizations(   # Display a set of VisualizationApps in pulldown menu
        classes, start=None, title="Datastructure Visualizations", version=None,
        adjustForTrinket=False, seed='3.14159', verbose=0, debug=False,
        theme='alt', introBG='white'):
    global DEBUG
    DEBUG = debug
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

    if adjustForTrinket:
        VAP.MIN_CODE_CHARACTER_HEIGHT = 9
    restoreMenu = Canvas(top, height=MIN_MENUBAR_HEIGHT, bg='pink')
    restoreMenu.grid(row=0, column=0, sticky=(N, E, W, S))
    menubutton = Menubutton(top, text='Select Visualization', font=MENU_FONT)
    menubutton.grid(row=0, column=0)
    restoreMenu.bind('<Enter>', makeArmMenuHandler(restoreMenu, menubutton))
    restoreMenu.bind('<Leave>', makeDisarmMenuHandler(restoreMenu, menubutton))
    
    padBy = abs(INTRO_FONT[1]) * 3
    labelStyleName='Intro.TLabel'
    top['bg'] = introBG
    intro = Frame(top, padx=padBy, pady=padBy, bg=introBG)
    nextline = makeIntro(
        intro_msg.format(
            customInstructions=(trinketInstructions if adjustForTrinket else 
                                desktopInstructions).strip()),
        intro, styleName=labelStyleName, bg=introBG,
        URLfg=None if adjustForTrinket else 'blue',
        URLfont=None if adjustForTrinket else INTRO_FONT + ('underline',) )
    loading = ttk.Label(intro, text='\nLoading ...', 
                        font=INTRO_FONT + ('italic',), style=labelStyleName)
    loading.grid(row=nextline, column=0)
    setattr(intro, 'appTitle', 'Introduction')
    appWindows.append(intro)
    top.bind('<Configure>', resizeHandler, '+')
    top.rowconfigure(1, minsize=600)
    top.columnconfigure(0, minsize=VAP.DEFAULT_CANVAS_WIDTH)
    intro.grid(row=1, column=0)
    
    menu = Menu(menubutton, tearoff=0)
    menu.add_command(label='Introduction', 
                     command=raiseAppWindowHandler(intro, menubutton, menu,
                                                   adjustForTrinket, sticky=()),
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
            try:
                vizApp = app(window=pane)
                vizApp.DEBUG = debug
                appTitle = getattr(vizApp, 'title', app.__name__)
                name = folder + ': ' + appTitle
                setattr(pane, 'appTitle', appTitle)
                appWindows.append(pane)
                pane.bind('<Map>', oneTimeShowHintHandler(vizApp), '+')
            except Exception as e:
                name = app.__name__ + ' *'
                msg = 'Error instantiating {}:\n{}'.format(app.__name__, e)
                label = Label(pane, text=msg, fg='red')
                label.grid()
                print(msg, file=sys.stderr)

            if start and start.lower() in (
                    getattr(vizApp, 'title', app.__name__).lower(),
                    app.__name__.lower()) and pane == appWindows[-1]:
               startAppWindow = pane
               
               pane.grid(row=1, column=0, sticky=(N, E, W, S))
               menu.entryconfigure(0, font=MENU_FONT)
               menubutton.grid_remove()
               
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

    if version:
        if isinstance(version, str):  # Hidden handler to show version info
            for button in range(1, 4):
                intro.bind('<Double-Button-{}>'.format(button),
                           lambda event:
                           (event.state & CTRL or
                            (isinstance(event.num, int) and event.num != 1)) and
                           loading.configure(text=version))
        elif isinstance(version, (tuple, list)):
            spacer = ttk.Label(intro, text=' ', font=INTRO_FONT,
                               style=labelStyleName)
            version = ttk.Label(intro, text='version {}.{}'.format(*version),
                                font=(INTRO_FONT[0], 2 - abs(INTRO_FONT[1])),
                                style=labelStyleName)
            spacer.grid(row=nextline + 1, column=0)
            version.grid(row=nextline + 2, column=0)
        else:
            raise ValueError('Version must be string or tuple/list, not {}'
                             .format(type(version)))
            
    loading['text'] = ''
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
        '-t', '--title',  default='Datastructure Visualizations',
        help='Title for top level window')
    parser.add_argument(
        '-w', '--warn-for-trinket', default=False, action='store_true',
        help='Adjust settings and warn users about limitations of use on '
        'Trinket.io')
    parser.add_argument(
        '--version', help='Version string or tuple to display on introduction')
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

    if (args.version and args.version.startswith('(') and
        args.version.endswith(')')):
        args.version = eval(args.version)
    showVisualizations(findVisualizations(args.files, args.verbose),
                       start=args.start, title=args.title, verbose=args.verbose,
                       adjustForTrinket=args.warn_for_trinket, debug=args.debug,
                       seed=args.seed, version=args.version)
