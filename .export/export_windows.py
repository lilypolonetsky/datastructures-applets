#! /usr/bin/env python3
__doc__ = '''
Export a self-contained Windows executable of all datastructure visualizations.
Run this in the directory where the visualization apps and associated PNG
files are stored.
'''

import PyInstaller.__main__
import sys, glob, os, argparse, subprocess, zipfile
from subprocess import CompletedProcess

if not hasattr(sys, 'path'): sys.path = []
for dir in ('.', '../PythonVisualizations'):
   if dir not in sys.path:
      sys.path.append(dir)

from export_common import *

def export_windows(
      appName: 'Base name of application to export'
      ='DatastructureVisualizations',
      version_file: 'JSON file containing the version tuple' = 'version.json',
      source_directory: 'Directory containing source and PNG files' = '.',
      icon: 'Path to icon file' ='design/Datastructure-Visualizations-icon.ico',
      ID: 'Bundle ID for Windows' ='com.shakumant.dev.{name}',
      zip_file: 'Zip archive name' ='{name}{version}.zip',
      sign_identity: 'Common name of codesign certificate' ='',
      keep: 'Keep executable source code file created for export.' =False,
      backup: 'File extension for backups of last export' ='.bak',
      work_dir: 'Directory for work files, .log, .pyz and etc.' ='./winbuild',
      distribution: 'Name of export distribution directory' ='./windist',
      verbose: 'Verbosity level of progress messages' =0):

   if verbose > 0:
      print('Verbosity level:', verbose)
   version = getVersion(version_file, verbose)
   appFilename = buildApplication(
      appName + '.py', version, source_directory=source_directory,
      verbose=verbose)
   
   iconfiles = set(glob.glob(icon))
   iconFilename = os.path.abspath(icon)
   zipFilename = zip_file.format(name=appName,
                                 version='_{:02d}_{:02d}'.format(*version))

   data_args = [
      '--add-data',
      os.path.join(os.path.abspath(source_directory), '*.png') + ';.',
      '--add-data',
      'C:/Program Files (x86)/Windows Kits/10/Redist/10.0.22000.0/ucrt/DLLs/x86/*.dll;.']


   specPath = os.path.dirname(distribution)
   backupFiles((work_dir, distribution, appName,
                os.path.join(specPath, appName) + '.spec', zipFilename),
               backup_extension=backup, verbose=verbose)

   logLevel = ['ERROR', 'WARN', 'INFO', 'DEBUG'][max(0, min(4, verbose))]
   PyInstallerArgs = [
      '--name', appName, '--distpath', distribution, '--workpath', work_dir,
      '--specpath', specPath, '--onefile', '--windowed', '--icon', iconFilename,
      '--log-level', logLevel ]
   if verbose > 1:
      printPyInstallerArguments(data_args, PyInstallerArgs)

   PyInstaller.__main__.run([appFilename, *data_args, *PyInstallerArgs])

   execFilename = os.path.join(distribution, appName + '.exe')
   if verbose > 0:
      print('Exported application is in {}'.format(execFilename))
      
   if zipFilename:
      archiveFilename = os.path.join(distribution, zipFilename)
      with zipfile.ZipFile(archiveFilename, 'w') as archive:
         archive.write(execFilename, arcname=os.path.basename(execFilename))
      print('Put application in {} archive'.format(archiveFilename))
   else:
      archiveFilename = ''

   if sign_identity:
      if verbose > 0:
         print('Signing exported application...')
      cmd = ['signtool', '-s', sign_identity,
             '-v', archiveFilename or execFilename]
      codesign_result = subprocess.run(cmd, capture_output=True, check=True)
      if verbose > 0:
         print('Result of command "{}":', ' '.join(cmd))
         for msg in (codesign_result.stdout, codesign_result.stderr):
            print(msg)
   
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
      '-s', '--source', default='.',
      help='Directory of source files and PNG images')
   parser.add_argument(
      '-i', '--icon', default='design/Datastructure-Visualizations-icon.ico',
      help='Path to icon file (relative to directory with visualizaion apps)')
   parser.add_argument(
      '--version-file', default='version.json',
      help='Name of JSON file containing the major and minor version numbers')
   parser.add_argument(
      '-I', '--ID', default='com.shakumant.dev.{name}',
      help='Bundle ID for Windows.  Can contain {name} string to be replaced '
      'with the base name of the executable.')
   parser.add_argument(
      '-z', '--zip-file', default='{name}{version}.zip',
      help='Disk image (dmg) name.  Can contain {name} string to be replaced '
      'with the base name of the executable and {version} in _major_minor '
      'format.')
   parser.add_argument(
      '--sign-identity', default='',
      help='Signer identity (common name of codesign certificate)')
   parser.add_argument(
      '-k', '--keep', default=False, action='store_true',
      help='Keep executable source code file created for export.')
   parser.add_argument(
      '-b', '--backup', default='.bak',
      help='File extension for backups of last export')
   parser.add_argument(
      '-w', '--work-dir', default='./winbuild',
      help='Directory for work files, .log, .pyz and etc.')
   parser.add_argument(
      '-d', '--distribution', default='./windist',
      help='Name of export distribution directory')
   parser.add_argument(
      '-v', '--verbose', action='count', default=0,
      help='Add verbose comments')
   args = parser.parse_args()

   export_windows(
      args.name, version_file=args.version_file,
      source_directory=args.source, icon=args.icon, ID=args.ID,
      zip_file=args.zip_file, sign_identity=args.sign_identity,
      keep=args.keep, backup=args.backup, work_dir=args.work_dir,
      distribution=args.distribution, verbose=args.verbose)
