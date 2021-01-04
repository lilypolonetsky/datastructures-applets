# Utilities for managing highlights on Tk text widgets corresponding
# to source code

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
       self.lines = self.code.split('\n')
       self.cache = {}
       self.textWidget = textWidget
       self.prefix = '{:04d}-'.format(self._counter)
       self.startMark = None
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

    def tag(self, fragment, copy=1):
        '''Tag name for a given fragment in this code block'''
        return '{}{}:{}'.format(self.prefix, fragment, copy)
    
    def findFragment(self, fragment, copy=1):
        '''Find a code fragment within the code block.  Look for the nth copy
        when there are multiple copies.  Return the line.char position of the
        start and end of the fragment, similar to the indices used by the
        Tk text widge, but use 0-relative line numbers.
        '''
        j = 0
        start = self.code.index(fragment) if fragment in self.code else None
        while start is not None and copy > 1:
            j = start + len(fragment)
            copy -= 1
            start = (j + self.code[j:].index(fragment)
                     if fragment in self.code[j:] else None)
        if start is not None:
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
        
    def markStart(self, ind='1.0'):
        '''Mark the start of this code block inside the Tk text widget'''
        self.startMark = self.prefix + '▶'
        self.textWidget.mark_set(self.startMark, ind)

if __name__ == '__main__':

    testCode='''
def factorial(n):
   if n < 1: return 1
   return (n *
           factorial(n - 1))
'''
    import VisualizationApp, sys
    app = VisualizationApp.VisualizationApp(title='Test Text Highlight')
    app.showCode(testCode)
    codeHighlightBlock = CodeHighlightBlock(testCode, app.codeText)
    codeHighlightBlock.markStart()
    for arg in reversed(sys.argv[1:]):
        app.showCode(arg, addBoundary=True)

    fragments = ['factorial(n)', 'n < 1', 'return', 'return', 'return', 
                 'return (n *\n           factorial(n - 1)', 'not here']
    tags = {}
    app.addAnimationButtons()
    app.startAnimations()
    app.setMessage('Finding fragments')
    app.wait(2)
    for i, fragment in enumerate(fragments):
        try:
            copy = 1 + i - fragments.index(fragment)
            tag = codeHighlightBlock[fragment] if copy == 1 else (
                codeHighlightBlock[fragment, copy])
            tags[fragment, copy] = tag
            print('Tag "{}" relative span is {}'.format(
                repr(tag), codeHighlightBlock.findFragment(fragment, copy)))
                
        except Exception as e:
            print('Unable to find copy {} of "{}".  Exception follows:\n{}'
                  .format(copy, fragment, e))

    try:
        app.setMessage('Highligting fragments in endless loop')
        app.wait(2)
        while True:
            for tag in tags:
                app.setMessage('Fragment "{}" copy {} has tag {}'.format(
                    tag[0], tag[1], repr(codeHighlightBlock[tag[0], tag[1]])))
                for othertag in tags:
                    app.codeText.tag_config(
                        tags[othertag],
                        background=app.CODE_HIGHLIGHT if tag is othertag else '')
                app.wait(1)
    except VisualizationApp.UserStop:
        print('Stop pressed')
    app.stopAnimations()
