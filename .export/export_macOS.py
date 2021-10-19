#! /usr/bin/env python3
__doc__ = '''
Export a self-contained macOS executable of all datastructure visualizations.
Run this in the directory where the visualization apps and associated PNG
files are stored.
'''

import PyInstaller.__main__
import sys, glob, os, shutil, argparse, subprocess, json
from subprocess import CompletedProcess

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
   '--version-file', default='.version',
   help='Name of JSON file containing the major and minor version numbers')
parser.add_argument(
   '-u', '--upgrade', choices=['major', 'minor'],
   help='Advance the major or minor version number read from the version file')
parser.add_argument(
   '-I', '--ID', default='com.shakumant.dev.{name}',
   help='Bundle ID for macOS.  Can contain {name} string to be replaced with'
   'the base name of the executable.')
parser.add_argument(
   '--disk-image', default='{name}{version}.dmg',
   help='Disk image (dmg) name.  Can contain {name} string to be replaced with'
   'the base name of the executable and {version} in _major_minor format. ')
parser.add_argument(
   '--sign-identity', default='Mac Developer',
   help='Signer identity (common name of codesign certificate)')
parser.add_argument(
   '-k', '--keep', default=False, action='store_true',
   help='Keep executable source code file created for export.')
parser.add_argument(
   '-b', '--backup', default='.bak',
   help='File extension for backups of last export')
parser.add_argument(
   '-d', '--distribution', default='dist',
   help='Name of export distribution directory')
parser.add_argument(
   '-v', '--verbose', action='count', default=0,
   help='Add verbose comments')
args = parser.parse_args()

if not hasattr(sys, 'path'): sys.path = []
sys.path.append('.')

if os.path.exists(args.version_file):
   with open(args.version_file, 'r') as vFile:
      version = json.load(vFile)
else:
   version = (1, 0)
if args.verbose > 0:
   print('Version read from {}'.format(args.version_file)
         if os.path.exists(args.version_file) else 'Version',
         'is {}.{}'.format(*version))

if args.upgrade:
   if args.upgrade == 'major':
      version = (version[0] + 1, 0)
   else:
      version = (version[0], version[1] + 1)
   print('Upgraded version is', '{}.{}'.format(*version))

pyfiles = set(glob.glob('*.py'))
toRemove = set(('runAllVisualizations.py', 'runAllVisualizationsMenu.py'))
pyfiles -= toRemove

pyfiles = set(glob.glob('*.py'))
pngfiles = set(glob.glob('*.png'))
appName = args.name
iconFilename = args.icon
iconfiles = set(glob.glob(iconFilename))
dmgFilename = args.disk_image.format(name=appName,
                                     version='_{:02d}_{:02d}'.format(*version))
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
   print('Verbosity level:', args.verbose)
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
            print('showVisualizations(({}), version={})'.format(', '.join(
               '{}.{}'.format(viz.__module__, viz.__name__)
               for viz in visualizations), version), file=appFile)
            break
         print(line, file=appFile, end='')
if args.verbose > 0:
   print('Created application file in', appFilename)

for item in (
      'build', args.distribution, appName, appName + '.spec', dmgFilename):
   if os.path.exists(item):
      if os.path.exists(item + args.backup):
         if args.verbose > 0:
            print('Removing', item + args.backup, '...')
            if os.path.isdir(item + args.backup):
               shutil.rmtree(item + args.backup)
            else:
               os.remove(item + args.backup)
      os.rename(item, item + args.backup)
         
if args.verbose > 1:
   print('PyInstaller arguments:')
   for arg in data_args:
      print(' ', arg, end='' if arg.startswith('-') else '\n')
      
PyInstaller.__main__.run([
   appFilename, *data_args,
   '--name', appName, '--distpath', args.distribution, '--windowed',
   '--osx-bundle-identifier', args.ID.format(name=appName),
   '--icon', iconFilename
])
os.rename(os.path.join(args.distribution, appName), appName)
if args.verbose > 1:
   print('Moved command line application {} from {}/ to .'.format(
      appName, args.distribution))
if args.verbose > 0:
   print('Exported application to {}/'.format(args.distribution))
if dmgFilename:
   hdiutil_result = subprocess.run(
      ['hdiutil', 'create', '-srcfolder', args.distribution,
       '-volname', appName, '-format', 'UDZO', dmgFilename],
      capture_output=True, check=True)
   codesign_result = subprocess.run(
      ['codesign', '-s', args.sign_identity, '-v', dmgFilename],
      capture_output=True, check=True
   ) if args.sign_identity else CompletedProcess((), 0)
   if args.verbose > 1:
      for msg in (hdiutil_result.stdout, hdiutil_result.stderr,
                  codesign_result.stdout, codesign_result.stderr):
         if msg:
            print(msg.decode())
   if args.verbose > 0:
      print('Created disk image', dmgFilename)

if args.version_file:
   with open(args.version_file, 'w') as vFile:
      json.dump(version, vFile)
   if args.verbose > 1:
      print('Wrote version {}.{} to {}'.format(*version, args.version_file))
   
if not args.keep:
   os.remove(appFilename)
elif args.verbose > 0:
   print('Kept application in', appFilename)
