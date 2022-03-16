#! /usr/bin/env python3
__doc__ = '''
Export a self-contained macOS executable of all datastructure visualizations.
Run this in the directory where the visualization apps and associated PNG
files are stored.
'''

import PyInstaller.__main__
import sys, glob, os, shutil, argparse, subprocess, json
from subprocess import CompletedProcess

def export_macOS(
      appName: 'Base name of application to export'
      ='DatastructureVisualizations',
      version_file: 'JSON file containing the version tuple' = 'version.json',
      icon: 'Path to icon file' ='design/Datastructure-Visualizations-icon.icns',
      ID: 'Bundle ID for macOS' ='com.shakumant.dev.{name}',
      disk_image: 'Disk image (dmg) name' ='{name}{version}.dmg',
      sign_identity: 'Common name of codesign certificate' ='',
      keep: 'Keep executable source code file created for export.' =False,
      backup: 'File extension for backups of last export' ='.bak',
      work_dir: 'Directory for work files, .log, .pyz and etc.' ='build',
      distribution: 'Name of export distribution directory' ='dist',
      verbose: 'Verbosity level of progress messages' =0):
   
   if not hasattr(sys, 'path'): sys.path = []
   sys.path.append('.')

   if os.path.exists(version_file):
      with open(version_file, 'r') as vFile:
         version = json.load(vFile)
   else:
      version = [1, 0]
   if verbose > 0:
      print('Version read from {}'.format(version_file)
            if os.path.exists(version_file) else 'Version',
            'is {}.{}'.format(*version))

   pyfiles = set(glob.glob('*.py'))
   toRemove = set(('runAllVisualizations.py', 'runAllVisualizationsMenu.py'))
   pyfiles -= toRemove
   pngfiles = set(glob.glob('*.png'))
   iconfiles = set(glob.glob(icon))
   dmgFilename = disk_image.format(name=appName,
                                   version='_{:02d}_{:02d}'.format(*version))

   try:
      import allVisualizationsCommon
      visualizations = allVisualizationsCommon.findVisualizations(
         pyfiles, max(0, verbose - 1))
   except ModuleNotFoundError:
      visualizations = []

   if any(len(s) == 0 for s in (visualizations, pngfiles, iconfiles)):
      print('Current directory =', os.getcwd())
      for files, kind in (
            (visualizations, 'Visualizations'),
            (pngfiles, 'PNG'),
            (iconfiles, 'Icon')):
         print('Could not find any {} files.'.format(kind) if len(files) == 0
               else 'Found {} {} file{}'.format(
                     len(files), kind, '' if len(files) == 1 else 's'))
      print('Is the current directory where the visualization files are?')
      raise Exception('Missing files for export')
   
   iconFilename = os.path.abspath(icon)

   if verbose > 0:
      print('Verbosity level:', verbose)
      print('Found {} python file{} and {} visualization app{}'.format(
         len(pyfiles), '' if len(pyfiles) == 1 else 's',
         len(visualizations), '' if len(visualizations) == 1 else 's'))
      if verbose > 1:
         for pyfile in pyfiles:
            vizClasses = [viz.__name__ for viz in visualizations
                          if (viz.__module__ + '.py') == pyfile]
            print(pyfile, '->' if vizClasses else '', ', '.join(vizClasses))

   data_args = ['--add-data', '{}:.'.format(os.path.join(os.getcwd(),'*.png'))]

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
   if verbose > 0:
      print('Created application file with {} visualiazation{} in {}'.format(
         len(visualizations), '' if len(visualizations) == 1 else 's',
         appFilename))

   specPath = os.path.dirname(distribution)
   if backup:
      for item in (
            work_dir, distribution, appName,
            os.path.join(specPath, appName) + '.spec', dmgFilename):
         if os.path.exists(item):
            if os.path.exists(item + backup):
               if verbose > 0:
                  print('Removing', item + backup, '...')
                  if os.path.isdir(item + backup):
                     shutil.rmtree(item + backup)
                  else:
                     os.remove(item + backup)
            os.rename(item, item + backup)

   logLevel = ['ERROR', 'WARN', 'INFO', 'DEBUG'][max(0, min(4, verbose))]
   PyInstallerArgs = [
      '--name', appName, '--distpath', distribution, '--workpath', work_dir,
      '--specpath', specPath, '--windowed', '--icon', iconFilename,
      '--log-level', logLevel,
      '--osx-bundle-identifier', ID.format(name=appName) ]
   if verbose > 1:
      print('PyInstaller arguments:')
      for arg in data_args:
         print(' ', arg, end='' if arg.startswith('-') else '\n')
      for i, arg in enumerate(PyInstallerArgs):
         print(' ', arg,
               end='\n' if (not arg.startswith('--') or
                            i >= len(PyInstallerArgs) - 1 or
                            PyInstallerArgs[i + 1].startswith('--')) else ' ')

   PyInstaller.__main__.run([appFilename, *data_args, *PyInstallerArgs])

   # os.rename(os.path.join(distribution, appName), appName)
   # if verbose > 1:
   #    print('Moved command line application {} from {}/ to .'.format(
   #       appName, distribution))
   if verbose > 0:
      print('Exported application is in {}'.format(
         os.path.join(distribution, appName, appName)))
      
   if dmgFilename:
      hdiutil_result = subprocess.run(
         ['hdiutil', 'create', '-srcfolder', distribution,
          '-volname', appName, '-format', 'UDZO', dmgFilename],
         capture_output=True, check=True)
      codesign_result = subprocess.run(
         ['codesign', '-s', sign_identity, '-v', dmgFilename],
         capture_output=True, check=True
      ) if sign_identity else CompletedProcess((), 0)
      if verbose > 0:
         for msg in (hdiutil_result.stdout, hdiutil_result.stderr,
                     codesign_result.stdout, codesign_result.stderr):
            if msg:
               print(msg.decode())
      if verbose > 0:
         print('Created disk image', dmgFilename)
   
   if not keep:
      os.remove(appFilename)
   elif verbose > 0:
      print('Kept application in', appFilename)

if __name__ == '__main__':
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
      '--version-file', default='version.json',
      help='Name of JSON file containing the major and minor version numbers')
   parser.add_argument(
      '-I', '--ID', default='com.shakumant.dev.{name}',
      help='Bundle ID for macOS.  Can contain {name} string to be replaced with'
      'the base name of the executable.')
   parser.add_argument(
      '--disk-image', default='{name}{version}.dmg',
      help='Disk image (dmg) name.  Can contain {name} string to be replaced '
      'with the base name of the executable and {version} in _major_minor '
      'format.')
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
      '-w', '--work-dir', default='build',
      help='Directory for work files, .log, .pyz and etc.')
   parser.add_argument(
      '-d', '--distribution', default='dist',
      help='Name of export distribution directory')
   parser.add_argument(
      '-v', '--verbose', action='count', default=0,
      help='Add verbose comments')
   args = parser.parse_args()

   export_macOS(
      args.name, args.version_file, args.icon, args.ID, args.disk_image,
      args.sign_identity, args.keep, args.backup, args.work_dir,
      args.distribution, args.verbose)
