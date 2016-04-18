"""Module with the implementation and related functions for the content
stack"""
from collections import namedtuple


class ContentStack(object):
    """A class to represent the content added as users drill into git revs,
    cycle through git history, show commits, etc"""
    def __init__(self):
        self.content_stack = []

    """These frames also store the state necessary to move back to the
    previous frame/screen when it is popped. Essentially storing a snapshot
    of what the screen looked like before we add this frame """
    StackFrame = namedtuple('StackFrame', ['content', 'last_current_line',
                                           'last_current_width',
                                           'last_cursor_line', 'last_mode'])

    def __len__(self):
        return len(self.content_stack)

    def peek(self):
        """Peek and return the content on the top of the stack,
        without removing it from the stack"""
        return self.content_stack[-1]

    def pop(self):
        """Pop content off the content stack, first checking if we have any
        extra content that can be popped (I.e. we don't want to be left]
        without any content to display to the user."""
        cstack = self.content_stack
        if len(cstack) <= 1:
            raise IndexError('No content to pop')
        frame_to_return = cstack.pop()
        self.content_stack[-1].content.decompress()
        return frame_to_return

    # pylint: disable=too-many-arguments
    def add(self, newcontent_obj, current_line, current_width,
            cursor_line, mode):
        """Add a new frame object to the Content Stack, preserving some of our
        current state as we do that, so it can be restored when we pop this."""
        # compress current stack before adding the new stack
        if len(self.content_stack) >= 1:
            self.content_stack[-1].content.compress()
        stack_frame = self.StackFrame(newcontent_obj, current_line,
                                      current_width, cursor_line, mode)
        self.content_stack.append(stack_frame)
