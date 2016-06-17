import sys
from libaws.base import platform

if platform.CURRENT_OS_SYSTEM == platform.WINDOWS_OS_SYSTEM:
    import ctypes

    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE= -11
    STD_ERROR_HANDLE = -12

    FOREGROUND_BLACK = 0x0
    FOREGROUND_BLUE = 0x01 # text color contains blue.
    FOREGROUND_GREEN = 0x02 # text color contains green.
    FOREGROUND_RED = 0x04 # text color contains red.
    FOREGROUND_INTENSITY = 0x08 # text color is intensified.

    BACKGROUND_BLUE = 0x10 # background color contains blue.
    BACKGROUND_GREEN = 0x20 # background color contains green.
    BACKGROUND_RED = 0x40 # background color contains red.
    BACKGROUND_INTENSITY = 0x80 # background color is intensified.

    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    std_err_handle = ctypes.windll.kernel32.GetStdHandle(STD_ERROR_HANDLE)
    
    std_handle_dict = {
        sys.stdout : std_out_handle,
        sys.stderr : std_err_handle 
    }

    Colors = {
        'red':FOREGROUND_RED,
        'blue':FOREGROUND_BLUE ,
        'green':FOREGROUND_GREEN, 
        'white':FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE,
        'black':FOREGROUND_BLACK 
    }

    class ColorPrinter:
        def __init__(self,stream = sys.stdout):
            self.handle = std_handle_dict[sys.stdout]
            self.stream = stream
    
        def set_cmd_color(self,color):
            """
                (color) -> bit
                Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
            """
            b = ctypes.windll.kernel32.SetConsoleTextAttribute(self.handle, color)
            return b

        def reset_color(self):
            self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

        def print_red_text(self,text,endline = True):
            self.print_color_text('red',text,endline)

        def print_green_text(self,text,endline = True):
            self.print_color_text('GREEN',text,endline)

        def print_blue_text(self,text,endline = True):
            self.print_color_text('blue',text,endline)

        def print_red_text_with_blue_bg(self,text,endline = True):
            self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY| BACKGROUND_BLUE | BACKGROUND_INTENSITY)
            if endline:
                text += "\n"
            self.stream.write(text)
            self.reset_color()
        
        def print_color_text(self,color,text,endline = True):
            color = color.lower()
            fore_color = Colors.get(color,0)
            self.set_cmd_color(fore_color | FOREGROUND_INTENSITY)
            if endline:
                text += "\n"
            self.stream.write(text)
            self.reset_color()
elif platform.CURRENT_OS_SYSTEM == platform.LINUX_OS_SYSTEM:

    from termcolor import colored

    class ColorPrinter:
        def __init__(self,stream = sys.stdout):
            self.stream = stream

        def print_green_text(self,text,endline = True):
            self.print_color_text("green",text,self.stream,endline)

        def print_red_text(self,text,endline = True):
            self.print_color_text("red",text,self.stream,endline)

        def print_blue_text(self,text,endline = True):
            self.print_color_text("blue",text,self.stream,endline)

        def print_color_text(self,color,text,endline = True):
            if endline:
                text += "\n"
            self.stream.write(colored(text,color))

