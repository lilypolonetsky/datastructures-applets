#! /usr/bin/env python3
__doc__ = '''
Export a self-contained macOS executable of all datastructure visualizations.
Run this in the directory where the visualization apps and associated PNG
files are stored.
'''

import PyInstaller.__main__
import sys, glob, os, argparse, subprocess, tempfile, shutil
from subprocess import CompletedProcess

if not hasattr(sys, 'path'): sys.path = []
for dir in ('.', '../PythonVisualizations'):
   if dir not in sys.path:
      sys.path.append(dir)

from export_common import *

def export_macOS(
      appName: 'Base name of application to export'
      ='DatastructureVisualizations',
      version_file: 'JSON file containing the version tuple' = 'version.json',
      source_directory: 'Directory containing source and PNG files' = '.',
      icon: 'Path to icon file' ='design/Datastructure-Visualizations-icon.icns',
      ID: 'Bundle ID for macOS' ='com.shakumant.dev.{name}',
      disk_image: 'Disk image (dmg) name' ='{name}{version}.dmg',
      sign_identity: 'Common name of codesign cert' ='Apple Distribution',
      keep: 'Keep executable source code file created for export.' =False,
      backup: 'File extension for backups of last export' ='.bak',
      work_dir: 'Directory for work files, .log, .pyz and etc.' ='./build',
      distribution: 'Name of export distribution directory' ='./dist',
      verbose: 'Verbosity level of progress messages' =0):

   if verbose > 0:
      print('Verbosity level:', verbose)
   version = getVersion(version_file, verbose)
   appFilename = buildApplication(
      appName + '.py', version, source_directory=source_directory,
      verbose=verbose)

   iconfiles = set(glob.glob(icon))
   iconFilename = os.path.abspath(icon)
   dmgFilename = disk_image.format(name=appName,
                                   version='_{:02d}_{:02d}'.format(*version))

   images = os.path.join(os.path.abspath(source_directory), '*.png')
   data_args = ['--add-data', images + ':.']

   specPath = os.path.dirname(distribution)
   backupFiles((work_dir, distribution, appName,
                os.path.join(specPath, appName) + '.spec', dmgFilename),
               backup_extension=backup, verbose=verbose)

   if sign_identity:
      if verbose > 0 and glob.glob(images):
         print('Codesigning images')
      for imageFile in glob.glob(images):
         imagesign_cmd = ['codesign', '-s', sign_identity, imageFile]
         if verbose > 1:
            print('Running:', ' '.join(imagesign_cmd), '  ...')
         result = subprocess.run(imagesign_cmd, capture_output=True)
         if result.returncode == 1 and result.stderr.decode().strip().endswith(
               'is already signed'):
            if verbose > 1:
               print('Ignoring reminder that file is already codesigned')
         elif result.returncode != 0:
            print('Error code from codesign =', result.returncode)
            for msg in (result.stdout, '-' * 77, result.stderr):
               text = (msg if isinstance(msg, str) else msg.decode()).strip()
               if text:
                  print(text)
         
   logLevel = ['ERROR', 'WARN', 'INFO', 'DEBUG'][max(0, min(4, verbose))]
   PyInstallerArgs = [
      '--name', appName, '--distpath', distribution, '--workpath', work_dir,
      '--specpath', specPath, '--windowed', '--icon', iconFilename,
      '--log-level', logLevel, '--target-arch', 'x86_64',
      '--osx-bundle-identifier', ID.format(name=appName) ]
   if sign_identity:
      PyInstallerArgs.extend(['--codesign-identity', sign_identity])

   if verbose > 1:
      printPyInstallerArguments(data_args, PyInstallerArgs)

   PyInstaller.__main__.run([appFilename, *data_args, *PyInstallerArgs])

   executable = os.path.join(distribution, appName + '.app')
   if verbose > 0:
      print('Exported application is in', executable)
      
   if dmgFilename:
      with tempfile.TemporaryDirectory() as tempdir:
         shutil.copytree(executable, os.path.join(tempdir, appName + '.app'))
         hdiutil_cmd = ['hdiutil', 'create', '-srcfolder', tempdir,
                        '-volname', appName, '-format', 'UDZO', dmgFilename]
         dmgsign_cmd = ['codesign', '-s', sign_identity, dmgFilename]
         if verbose > 0:
            dmgsign_cmd[-1:-1] = ['-v']
         commands = [hdiutil_cmd, dmgsign_cmd] if sign_identity else [
            hdiutil_cmd]
         if verbose > 1:
            print('About to run the following command sequence:')
            for cmd in commands:
               print(' ', ' '.join(commandLineArg(x) for x in cmd))
         results = [
            subprocess.run(cmd, capture_output=True) for cmd in commands]
         if verbose > 0 or any(result.returncode != 0 for result in results):
            for cmd, result in zip(commands, results):
               print('=' * 77, '\nExecution of',
                     ' '.join(commandLineArg(x) for x in cmd),
                     'returned code', result.returncode,
                     'success!' if result.returncode == 0 else 'error!')
               for msg in (result.stdout, '-' * 77, result.stderr):
                  text = (msg if isinstance(msg, str) else msg.decode()).strip()
                  if text:
                     print(text)
         for cmd, result in zip(commands, results):
            if result.returncode != 0:
               raise Exception(
                  'Exit code {} during: {}'.format(
                     result.returncode,
                     ' '.join(commandLineArg(x) for x in cmd)))

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
      '-s', '--source', default='.',
      help='Directory of source files and PNG images')
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
      '--sign-identity', default='Apple Distribution',
      help='Signer identity (common name of codesign certificate)')
   parser.add_argument(
      '-k', '--keep', default=False, action='store_true',
      help='Keep executable source code file created for export.')
   parser.add_argument(
      '-b', '--backup', default='.bak',
      help='File extension for backups of last export')
   parser.add_argument(
      '-w', '--work-dir', default='./build',
      help='Directory for work files, .log, .pyz and etc.')
   parser.add_argument(
      '-d', '--distribution', default='./dist',
      help='Name of export distribution directory')
   parser.add_argument(
      '-v', '--verbose', action='count', default=0,
      help='Add verbose comments')
   args = parser.parse_args()

   export_macOS(
      args.name, version_file=args.version_file,
      source_directory=args.source, icon=args.icon, ID=args.ID,
      disk_image=args.disk_image, sign_identity=args.sign_identity,
      keep=args.keep, backup=args.backup, work_dir=args.work_dir,
      distribution=args.distribution, verbose=args.verbose)
