#! /usr/bin/env python3
__doc__ = '''
Export a self-contained macOS executable of all datastructure visualizations.
Run this in the directory where the visualization apps and associated PNG
files are stored.
'''

import PyInstaller.__main__
import sys, glob, os, shutil, argparse

parser = argparse.ArgumentParser(
   description=__doc__,
   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
   '-n', '--name', default='DatastructureVisualizations',
   help='Base name of execcutable')
parser.add_argument(
   '-i', '--icon', default='design/Datastructure-Visualizations-icon.icns',
   help='Path to icon file (relative to directory with visualizaion apps)')
parser.add_argument(
   '-k', '--keep', default=False, action='store_true',
   help='Keep executable source code file created for export.')
parser.add_argument(
   '-b', '--backup', default='.bak',
   help='File extension for backups of last export')
parser.add_argument(
   '-v', '--verbose', action='count', default=0,
   help='Add verbose comments')
args = parser.parse_args()

if not hasattr(sys, 'path'): sys.path = []
sys.path.append('.')

args.verbose = 1
pyfiles = set(glob.glob('*.py'))
toRemove = set(('runAllVisualizations.py', 'runAllVisualizationsMenu.py'))
pyfiles -= toRemove

pyfiles = set(glob.glob('*.py'))
pngfiles = set(glob.glob('*.png'))
appName = args.name
iconFilename = args.icon
iconfiles = set(glob.glob(iconFilename))
for files, name in (
      (pyfiles, 'Python'), (pngfiles, 'PNG'), (iconfiles, 'Icon')):
   if len(files) == 0:
      print('Could not find any {} files.'.format(name))

try:
   import allVisualizationsCommon
   visualizations = allVisualizationsCommon.findVisualizations(
      pyfiles, args.verbose)
except ModuleNotFoundError:
   visualizations = []

if any(len(s) == 0 for s in (visualizations, pngfiles, iconfiles)):
   print('Current directory =', os.getcwd())
   print('Is the current directory set to where the visualization files are?')
   print('Exiting.')
   sys.exit(-1)
   
iconFilename = os.path.abspath(iconFilename)

if args.verbose > 0:
   print('Found {} python file{}'.format(
      len(pyfiles), '' if len(pyfiles) == 1 else 's'))
   if args.verbose > 1:
      for pyfile in pyfiles:
         print(pyfile)
      print('Visualizations:')
      for viz in visualizations:
         print(viz.__module__)

data_args = ['--add-data', '*.png:.']

appFilename = appName + '.py'
model = 'runAllVisualizationsMenu.py'
with open(appFilename, 'w') as appFile:
   with open(model, 'r') as modelFile:
      for line in modelFile:
         if line.startswith("if __name__ == '__main__':"):
            print('import {}'.format(', '.join(
               viz.__module__ for viz in visualizations)), file=appFile)
            print('showVisualizations(({}))'.format(', '.join(
               '{}.{}'.format(viz.__module__, viz.__name__)
               for viz in visualizations)), file=appFile)
            break
         print(line, file=appFile, end='')
if args.verbose > 0:
   print('Created application file in', appFilename)

for item in ('build', 'dist', appName + '.spec'):
   if os.path.exists(item):
      if os.path.exists(item + args.backup):
         if args.verbose > 0:
            print('Removing', item + args.backup, '...')
            if os.path.isdir(item + args.backup):
               shutil.rmtree(item + args.backup)
            else:
               os.remove(item + args.backup)
      os.rename(item, item + args.backup)
         
if args.verbose > 0:
   print('PyInstaller arguments:')
   for arg in data_args:
      print(' ', arg, end='' if arg.startswith('-') else '\n')
      
PyInstaller.__main__.run([
   appFilename, *data_args,
   '--name', appName,
   '--windowed',
   '--osx-bundle-identifier', 'com.shakumant.dev.{}'.format(appName),
   '--icon', iconFilename
])
if args.verbose > 0:
   print('Exported application to dist/')

if not args.keep:
   os.remove(appFilename)
elif args.verbose > 0:
   print('Kept application in', appFilename)
