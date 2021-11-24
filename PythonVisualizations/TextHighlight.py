# Utilities for managing highlights on Tk text widgets corresponding
# to source code

import re

declarationPattern = re.compile(r'^\s*(def|class)\s+(\w+)(\W|$)')

class CodeHighlightBlock(object):
    '''Class to hold information about visualizing the code during animation
    of a particular call on the call stack.  After creating a block,
    the Tk text widiget indices 
    '''

    _counter = 1
    
    def __init__(self,       # Constructor takes code block, assigns it
                 code,       # a unique prefix to highlight snippets in it,
                 textWidget): # and tags the snippets when refreenced
       self.code = code.strip()
       self.lines = self.code.split('\n') if len(code) > 0 else []
       declaration = self.lines and declarationPattern.match(self.lines[0])
       self.blockName = declaration and declaration.group(2)
       self.cache = {}
       self.textWidget = textWidget
       self.prefix = '{:04d}-'.format(self._counter)
       self.startMark = None
       self.currentFragments = None
       CodeHighlightBlock._counter += 1

    def __getitem__(self, fragment):
       if not isinstance(fragment, tuple):
           fragment = (fragment, 1)
       if fragment in self.cache:
           return self.cache[fragment]
       if self.startMark is None:
           raise KeyError('Missing start mark for CodeHighlightBlock')
       span = self.findFragment(*fragment)
       if span:
           if self.startMark in self.textWidget.mark_names():
               startLine = int(
                   self.textWidget.index(self.startMark).split('.')[0])
               newspan = ['{}.{}'.format(startLine + int(line), char)
                          for line, char in [ind.split('.') for ind in span]]
               tag = self.tag(*fragment)
               self.textWidget.tag_add(tag, *newspan)
               self.cache[fragment] = tag
               return tag
           else:
               raise KeyError('Start mark "{}" no longer in CodeHighlightBlock'
                              .format(self.startMark))
       else:
           raise KeyError('Snippet "{}" copy {} not found in code block'.format(
               *fragment))

    def __str__(self):
        return '<CodeHighlightBlock: {} {}>'.format(self.blockName, id(self))

    def tag(self, fragment, copy=1):
        '''Tag name for a given fragment in this code block'''
        return '{}{}:{}'.format(self.prefix, fragment, copy)
    
    def findFragment(self, fragment, copy=1):
        '''Find a code fragment within the code block.  Look for the nth copy
        when there are multiple copies.  Return the line.char position of the
        start and end of the fragment, similar to the indices used by the
        Tk text widget, but use 0-relative line numbers.
        For regex fragments that have parenthesized groups, find the indices
        of the last, non-empty group in the match.
        '''
        j = 0
        if isinstance(fragment, type(declarationPattern)):
            matches = [match for match in fragment.finditer(self.code)]
            if len(matches) >= copy:
                match = matches[copy - 1]
                lastGroup = 0
                for i in range(1, len(match.groups()) + 1):
                    if match.group(i):
                        lastGroup = i
                start = match.start(lastGroup)
                fragment = match.group(lastGroup)
            else:
                start = None
        else:
            start = self.code.index(fragment) if fragment in self.code else None
            while start is not None and copy > 1:
                j = start + len(fragment)
                copy -= 1
                start = (j + self.code[j:].index(fragment)
                         if fragment in self.code[j:] else None)
        if start is None:
            return None
        chars, line = 0, 0
        while (line < len(self.lines) and
               chars + len(self.lines[line]) < start):
            chars += len(self.lines[line]) + 1
            line += 1
        if line >= len(self.lines) or chars >= len(self.code):
            raise IndexError(
                'Internal error.  No more lines or characters when finding '
                'fragment "{}"'.format(fragment))
        first = '{}.{}'.format(line, start - chars)
        while (line < len(self.lines) and
               chars + len(self.lines[line]) < start + len(fragment)):
            chars += len(self.lines[line]) + 1
            line += 1
        if line >= len(self.lines) or chars >= len(self.code):
            raise IndexError(
                'Internal error.  No more lines or characters when finding '
                'fragment "{}"'.format(fragment))
        return first, '{}.{}'.format(line, start + len(fragment) - chars)
        
    def markStart(self, ind='1.0', resetCache=True):
        '''Mark the start of this code block inside the Tk text widget'''
        self.startMark = self.prefix + '▶'
        self.textWidget.mark_set(self.startMark, ind)
        if resetCache:
            self.cache = {}

def getCodeHighlightBlock(seq):
    'Utility to find the first CodeHighlightBlock within a sequence'
    for item in seq:
        if isinstance(item, CodeHighlightBlock):
            return item

if __name__ == '__main__':

    try:
        from tkUtilities import *
    except ModuleNotFoundError:
        from .tkUtilities import *

    testCode='''
def factorial(n):
   if n < 1: return 1
   return (n *
           factorial(n - 1))
'''
    from tkinter import *
    import VisualizationApp, sys
    app = VisualizationApp.VisualizationApp(
        title='Test Text Highlight', canvasBounds=(0, 0, 1200, 600))

    x, y = 10, 10
    def canvasPrint(*texts, sep=' '):
        global app, x, y
        text = sep.join(map(str, texts))
        for line in text.split('\n'):
            app.canvas.create_text(
                x, y, anchor=NW, text=line, font=app.VARIABLE_FONT,
                fill=app.VARIABLE_COLOR)
            y += textHeight(app.VARIABLE_FONT)

    fragments = ['factorial(n)', 'n < 1', 'return', 'return', 'return', 
                 'return (n *\n           factorial(n - 1)',
                 re.compile(r'return \(n \*\s+factorial'),
                 (re.compile(r'\W(n)\W'), 3), re.compile(r'\s(1)\s'),
                 'not here', re.compile(r'not here')]
    tags = {}
    useHighlightCode = IntVar()
    useHighlightCode.set(1)
    useHighlightCodeButton = Checkbutton(
        app.operations, text="Use highlightCode", variable=useHighlightCode)
    useHighlightCodeButton.grid(column=4, row=1, padx=8, sticky=(E, W))
    app.addAnimationButtons()

    callEnviron = app.createCallEnvironment(testCode)
    codeHighlightBlock = CodeHighlightBlock(testCode, app.codeText)
    codeHighlightBlock.markStart()
    canvasPrint('Added', codeHighlightBlock)
    for arg in reversed(sys.argv[1:]):
        app.showCode(arg, addBoundary=True)

    app.setMessage('Finding fragments')
    for i, fragment in enumerate(fragments):
        try:
            fragTuple = fragment if isinstance(fragment, tuple) else (
                fragment, 1 + i - fragments.index(fragment))
            copy = fragTuple[1]
            tag = (codeHighlightBlock[fragment] if copy == 1 else
                   codeHighlightBlock[fragTuple])
            tags[fragTuple] = tag
            canvasPrint('Tag "{}" relative span is {}'.format(
                repr(tag), codeHighlightBlock.findFragment(*fragTuple)))
                
        except (IndexError, KeyError) as e:
            canvasPrint(
                'Unable to find copy {} of "{}".  Exception was:\n{}'.format(
                    copy, fragment, e))

    try:
        canvasPrint('\nHighligting fragments in endless loop...')
        while True:
            for tag in tags:
                widgetState(useHighlightCodeButton, NORMAL)
                app.setMessage('Fragment "{}" copy {}\nhas tag {}'.format(
                    tag[0], tag[1], repr(codeHighlightBlock[tag[0], tag[1]])))
                if useHighlightCode.get():
                    app.highlightCode(tag, callEnviron)
                else:
                    for othertag in tags:
                        app.codeText.tag_config(
                            tags[othertag],
                            background=app.CODE_HIGHLIGHT if tag is othertag
                            else '')
                app.wait(0 if app.animationsStepping() else 1)
    except VisualizationApp.UserStop:
        print('Stop pressed')
    app.stopAnimations()
