#!/usr/bin/env python3

__doc__ = """Make a version of the python-visualizations that's easy to
export to trinket.io
"""

import argparse, sys, os, glob, shutil, re, git, time

specialContent = {
   'main.py': '''
from runAllVisualizationsMenu import *

showVisualizations(
    findVisualizations('.'),
    title='Algorithm Visualizations', version={version!r},
    adjustForTrinket=True)
'''
   }

mustHave = ['VisualizationApp.py']
replacements = [('▶', '=left_arrow='), ('▢', 'W'), ('✓', 'X'), ('ø', '!'),
                ('∞', 'inf')]
excludeDefaults = [r'__init__.*', r'.*[Tt]est.*', r'runAllVisualizations\.py']
cleanDefaults = [r'.*\.py']

repository_directory = os.path.dirname(
   os.path.abspath(os.path.dirname(sys.argv[0])))
source_directory = os.path.join(repository_directory, 'PythonVisualizations')

def export_trinket(
      outdir: 'Output directory for trinket files',
      source_directory: 'Directory containing source and PNG files' = '.',
      verbose: 'Verbosity level for progress messages: 0 is lowest' =0,
      ignore: 'Ignore files with non-ASCII characters after cleansing' =False,
      force: 'Allow export if git working tree is dirty or outdir exists' =False,
      exclude: 'Regexes for filenames to exclude from export' =[],
      clean: 'Regexes for filenames to clean of non-ASCII characters' = [],
      repo: 'Git repository object' =None,
      repoBranch: 'Branch in git repository being exported' ='HEAD'):

   if not all(os.path.exists(os.path.join(source_directory, f))
              for f in mustHave):
      msg =('Missing some files.  Expected to find: {}\n'
            'Is the source directory, {}, correct?').format(
               ', '.join(mustHave), source_directory)
      raise Exception(msg)
      
   if repo is None:
      repoDir = os.path.dirname(os.path.abspath(source_directory))
      try:
         repo = git.Repo(repoDir)
      except Exception as e:
         raise Exception(
            'Could not find git repository object in {} directory.\n{}'.format(
            repoDir, e))
   if repo.is_dirty():
      if not force:
         raise Exception(
            'Git working directory, {}, has unsaved changes'.format(
               repo.working_dir))
      elif verbose > 0:
         print('Ignoring unsaved changes to git working directory: {}'.format(
            repo.working_dir))
   lastCommit = repo.commit(repoBranch)
   versionString = '{} {} {}\n{} UTC'.format(
      lastCommit.summary, lastCommit.hexsha[:7], lastCommit.author.name,
      time.asctime(time.gmtime(lastCommit.committed_date)))
   if verbose > 0:
      print('Version info: "{}"'.format(versionString))
         
   if os.path.exists(outdir):
      if os.path.isdir(outdir) and force:
         if verbose > 0:
            print('Clearing {} directory'.format(outdir))
         shutil.rmtree(outdir)
         os.mkdir(outdir)
      elif os.path.isdir(outdir):
         print('{} exists.  Use --force option to clear contents first'.format(
            outdir))
         sys.exit(0)
      else:
         print('{} is not a directory.{}'.format(
            outdir, 'Ignoring --force' if force else ''))
         sys.exit(-1)
   else:
      if verbose > 0:
         print('Creating {} directory'.format(outdir))
      os.mkdir(outdir)

   files = glob.glob(os.path.join(source_directory,'*.py')) + glob.glob(
      os.path.join(source_directory, '*.png'))
   for filename in files:
      basename = os.path.basename(filename)
      if basename in specialContent:
         print('Skipping export of {}'.format(filename))
         continue

      if any(regex.match(basename) for regex in exclude):
         if verbose > 0:
            print('Excluding {} for match to an exclude pattern'.format(
               basename))
         continue
      
      if any(regex.match(basename) for regex in clean):
         with open(filename, 'r') as infile:
            content = infile.read()
            revised = content
            for pair in replacements:
               revised = revised.replace(*pair)
            containsNonASCII = any(ord(c) > 127 for c in revised)
            if containsNonASCII and not ignore:
               print('=' * 70, '\n',
                     ('File {} contains some non-ASCII characters '
                      'after replacements').format(basename),
                     '\n' + '=' * 70)
            if verbose > 0:
               print('Exporting {}{}{}'.format(
                  basename, ' with substitions' if content != revised else '',
                  ' ignoring lingering non-ASCII characters' 
                  if containsNonASCII and ignore else ''))
            with open(os.path.join(outdir, basename), 'w') as outfile:
               outfile.write(revised)
               outfile.close()
      else:
         if verbose > 0:
            print('Copying {} verbatim'.format(basename))
         shutil.copyfile(filename, os.path.join(outdir, basename))
      
   for basename in specialContent:
      if verbose > 0:
         print('Creating {}'.format(basename))
      with open(os.path.join(outdir, basename), 'w') as outfile:
         outfile.write(specialContent[basename].format(version=versionString))
         outfile.close()
         
   print('Created export in {}'.format(outdir))
   
if __name__ == '__main__':
   parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument(
      'output_directory', nargs=1, help='Directory to put trinket export in')
   parser.add_argument(
      '-s', '--source', default=source_directory,
      help='Directory containing source Python and PNG files')
   parser.add_argument(
      '-f', '--force', default=False, action='store_true',
      help='Clear existing output and ignore unclean git working directories')
   parser.add_argument(
      '-c', '--clean', nargs='*', default=cleanDefaults,
      help='Regex for filenames whose non-ASCII characters should be cleaned')
   parser.add_argument(
      '-i', '--ignore', default=False, action='store_true',
      help='Ignore files with non-ASCII characters after cleansing')
   parser.add_argument(
      '-x', '--exclude', nargs='*', default=excludeDefaults,
      help='Regex for filenames to exclude from export')
   parser.add_argument(
      '-v', '--verbose', action='count', default=0,
      help='Add verbose comments')
   args = parser.parse_args()

   export_trinket(
      args.output_directory[0], source_directory=args.source,
      verbose=args.verbose, ignore=args.ignore, force=args.force,
      exclude=[re.compile(exp) for exp in args.exclude],
      clean=[re.compile(exp) for exp in args.clean])
