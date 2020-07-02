# Visualizing the code stack and cleaning up stack frames

The initial design of the code text window and the cleanup system
assumed there was a single animation being run from a single chunk of
source code.  The reality is that one animation/method calls other
animations/methods to do some work, pushing them on the call stack.
The top of the call stack is the one in active execution and animates
most of the canvas items while highlighting code snippets being
executed.  There might be other canvas items from lower parts of the
stack that could either A) countinue being visible, or B) be
temporarily hidden for restoration once control returns to that frame.

Internally, VisualizationApp can manage a stack of local environments.
The `self.cleanup` attribute would become `self.callStack` and each of its
items would be a set of all the items that need to go away
when the function returns/exits.  If users press Stop in the middle of
an animation, the sysem would clean up all the callStack structures via
a try/except handler set up by `addOperation()`.  The wait routine would throw
an exception that is caught by the addOperation handler.

The `addOperation()` method would also take care of completely cleaning up
anything left on the callStack before invoking the operation function passed
as an argument.  This allows the initial button to clean up everything left
visible from a top-level operation, shifts responsibility for cleaning
up one level of the callStack to the separate visualization modules, and
allows for leaving some items visible ever after the animation stops (e.g.
the outermost code).

Each invocation of an animation method would:
* push a new set on the callStack
* put new local variable structures in the top set of the callStack
* put a new code text structure into the top set of the callStack
* call cleanUp on just the top of the callStack when it finishes

Leaving the items on the callStack as sets that the caller can manipulate
opens them up to being changed in unexpected ways, but leaves the
syntax of adding items or unioning a set of items easy.  Removing items
is just as easy.  

## Showing a stack in the code window

Each call to an animation method could show code and highlight it
during "execution".  The code would go in a block of lines in the text
window.  The current block being executed would always be on top.

The call to highlight a snippet would need to uniquely identify the
callStack so that recursive calls could be handled separately.  That
will require unique tags for each call.  The code text structure on
top of the stack would provide a unique prefix for all the snippets it
highlights.  When a call to an animation begins it would create the
local environment on top of the stack along with information about the
code and the snippets to be highlighted.  The `showCode()` and
`createCodeTags()` should be merged into a single method that creates
the local environment associated with the animation method that calls
it.  Let's call the code text structure a `CodeHighlightBlock` and
store it inside the call stack set.

Presumably,
the highlighted tags in calls below the topmost of the call stack
should stay highlighted while the topmost call "runs".
That requires changing the logic that turns off highlighting everything but
the requested tag(s) passed to `highlightCodeTags()`.  The new logic would  
only affect highlghts for the topmost call stack set.

If new code chunks are always inserted at the top of the text widget
then the _<line>.<character>_ tag boundary indices will be correct for
the text at the top.  Tk will then take care of keeping the tag with the
corresponding characters in the text widget as lines are added or removed
(only at the top of the stack).

We can use some kind of boundary line of text between calls on the
call stack, probably with a different background color.  They can span
the entire width of of the text widget.  If the text widget shrinks in
width, the boundary lines will wrap, but that's not an issue worth
worrying about yet.  The background color and maybe other display
aspects can be managed with a tag that gets added by `showCode()`.

The `CodeHighlightBlock` needs to keep the line count
of the code that was inserted for the call.  The first code block
inserted into the code window probably should not get a boundary line
since that will be an unnecessary distraction.  Code that gets inserted
must terminate with a newline if a boundary line follows.

## API

A new animation should have to only make one or two method calls at
the beginning to create the new local environment on the callStack.
The call(s) should produce a `set` to which animation items can be
added for later clean up.  For example:

```
    def bubbleSort(self):
        callEnv = self.createCallEnvironment(code, codeSnippets)
	...
	callEnv.add(self.canvas.create_text(*coords, text="myVar"))
        ...
        self.highlightCodeTags(callEnv, 'key_comparison')
        ...
	self.cleanUp(callEnv)
	return
```

The `createCallEnvironment()` builds the set that gets pushed on the
`callStack` and is the value returned.  If the animation method has
code to show and snippets to highlight, they are passed in here.
The `cleanUp()` at the end takes the callEnv set and removes its display
items.

What about a recursive procedure that shows multiple copies of the
same variables as canvas items for the different invocations?  It
would be nice if we could dim, gray out, or hide the canvas items from
lower calls on the stack, then restore them once the recursive call
returns.  Hiding them could be achieved by moving them fully off the
canvas and then back again by the reverse move.  If left on the
canvas, they will cause confusion.  The caller could wrap recursive
calls with something like:

```
   def Fibonacci(self, N):
        callEnv = self.createCallEnvironment()
	callEnv.add(self.canvas.create_text(*coords, text="N"))
	...
	if N > 1:
            self.hideCallEnv(callEnv)
            f_of_N_1 = self.Fibonacci(N-1)
            self.showCallEnv(callEnv)
	...
	self.cleanUp(callEnv)
```