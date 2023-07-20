#! /usr/bin/env python3
__doc__ = '''
Utilties common to macOS and Windows exports
Run this in the directory where the visualization apps and associated PNG
files are stored.
'''

import sys, glob, os, shutil, json

class Hidden(object):
   def __init__(self, thing):
      self.thing = thing

   def __str__(self):
      return '*HIDDEN*'

def commandLineArg(thing):
   'Get the string representation for printing a command line argument'
   return ('{!r}'.format(thing) if isinstance(thing, str) and ' ' in thing
           else str(thing))

def makeCommand(args):
   'Replace any hidden items with the actual value in command line arguments'
   return [item.thing if isinstance(item, Hidden) else item for item in args]

if not hasattr(sys, 'path'): sys.path = []
for dir in ('.', '../PythonVisualizations'):
   if dir not in sys.path:
      sys.path.append(dir)

try:
   from allVisualizationsCommon import *
except ModuleNotFoundError:
   from .allVisualizationsCommon import *

def getVersion(version_file, verbose=0):
   if os.path.exists(version_file):
      with open(version_file, 'r') as vFile:
         version = json.load(vFile)
   else:
      version = [1, 0]
   if verbose > 0:
      print('Version read from {}'.format(version_file)
            if os.path.exists(version_file) else 'Version',
            'is {}.{}'.format(*version))
   return version
   
def buildApplication(
      appName: 'File name of application to export',
      version: 'Version in the form of a string or list of numbers',
      source_directory: 'Path to source file directory' = '.',
      verbose: 'Verbosity level of progress messages' =0):
   
   if not hasattr(sys, 'path'): sys.path = []
   if source_directory not in sys.path:
      sys.path.append(source_directory)

   pyfiles = set(glob.glob(os.path.join(source_directory, '*.py')))
   toRemove = set()
   exportPyFiles = set(f for f in pyfiles if os.path.basename(f) not in
                       ('runAllVisualizations.py', 'runAllVisualizationsMenu.py'))
   pngfiles = set(glob.glob(os.path.join(source_directory, '*.png')))

   visualizations = findVisualizations(pyfiles, max(0, verbose - 1))

   if any(len(s) == 0 for s in (visualizations, pngfiles)):
      print('Source directory = {!r}'.format(source_directory))
      for files, kind in (
            (visualizations, 'Visualizations'),
            (pngfiles, 'PNG')):
         print('Could not find any {} files.'.format(kind) if len(files) == 0
               else 'Found {} {} file{}'.format(
                     len(files), kind, '' if len(files) == 1 else 's'))
      print('Is the source directory where the visualization files are?')
      raise Exception('Missing files for export')
   
   if verbose > 0:
      print('Found {} python file{} and {} visualization app{}'.format(
         len(pyfiles), '' if len(pyfiles) == 1 else 's',
         len(visualizations), '' if len(visualizations) == 1 else 's'))
      if verbose > 1:
         for pyfile in pyfiles:
            vizClasses = [
               viz.__name__ for viz in visualizations
               if (viz.__module__ + '.py') == os.path.basename(pyfile)]
            print(pyfile, '->' if vizClasses else '', ', '.join(vizClasses))

   appFilename = appName
   model = os.path.join(source_directory, 'runAllVisualizationsMenu.py')
   with open(appFilename, 'w') as appFile:
      with open(model, 'r') as modelFile:
         for line in modelFile:
            if line.startswith("if __name__ == '__main__':"):
               print('import {}'.format(', '.join(
                  viz.__module__ for viz in visualizations)), file=appFile)
               print('showVisualizations(({}), version={})'.format(', '.join(
                  '{}.{}'.format(viz.__module__, viz.__name__)
                  for viz in visualizations), version), file=appFile)
               break
            print(line, file=appFile, end='')
   if verbose > 0:
      print('Created application file with {} visualiazation{} in {}'.format(
         len(visualizations), '' if len(visualizations) == 1 else 's',
         appFilename))
   return appFilename

def backupFiles(
      filesToBackup: 'Files or directories to backup',
      backup_extension: 'File extension for backed up copy' = '.bak',
      verbose: 'Verbosity level of progress messages' =0):
   
   for item in filesToBackup:
      if os.path.exists(item):
         backup_item = item + backup_extension
         if os.path.exists(backup_item):
            if verbose > 0:
               print('Removing', backup_item, '...')
            if os.path.isdir(backup_item):
               shutil.rmtree(backup_item)
            else:
               os.remove(backup_item)
         if verbose > 0:
            print('Renaming', item, 'to', backup_item)
         os.rename(item, backup_item)

def printPyInstallerArguments(data_args, PyInstallerArgs, prefix=' '):
   print('PyInstaller arguments:')
   for arg in data_args:
      print(prefix, arg, end='' if arg.startswith('-') else '\n')
   for i, arg in enumerate(PyInstallerArgs):
      option = arg.startswith('--')
      end = i >= len(PyInstallerArgs) - 1
      if option:
         print(
            prefix, arg,
            end='\n' if end or PyInstallerArgs[i + 1].startswith('--') else ' ')
      else:
         print(repr(arg))
