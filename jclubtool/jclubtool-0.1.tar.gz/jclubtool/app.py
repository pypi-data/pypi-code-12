import tkinter as tk
from PIL import Image, ImageTk
from .pages import PageCollection
from .guitools import SelectionBox
from . import io
from tkinter import filedialog, messagebox, ttk
import os
from os import path


class Application(tk.Frame):

    def __init__(self, images=None, master=None, save_dir=io.user_home_dir, debug=False):

        tk.Frame.__init__(self, master=master)
        self.grid(row=0, column=0)

        self.images = None

        self._createWidgets()
        self.img_dirname.set(save_dir)

        self.selectbox = SelectionBox(self.canvas)
        if debug:
            self.load_pdf(filename=path.join('samples', '416.full.pdf'),
                          resolution=50)
        else:
            self.load_pdf()

    def load_pdf(self, filename=None, load_dir=io.user_home_dir, resolution=100):
        if not filename:
            filename = filedialog.askopenfilename(initialdir=load_dir,
                                                  filetypes=[('pdf files', '*.pdf')])
            if not filename:
                return

        io.clear_cache()
        io.copy_file_to_cache(filename)
        new_filename = path.join(io.cache_dir, path.basename(filename))
        io.convert_pdf_to_jpg(new_filename, path.join(io.cache_dir, 'img'),
                              resolution=resolution)
        img_names = io.get_jpg_filenames_from_cache()
        self.img_dirname.set(path.dirname(filename))

        images = [Image.open(name) for name in img_names]
        self.images = PageCollection(images)
        self.images.set_scale(self.canvas.winfo_height())
        self.show_img()

    def _createWidgets(self, width=600, height=700):
        """Setup method.  Creates all buttons, canvases, and defaults before starting app."""

        self.bar = tk.Frame(self)
        self.bar.pack()#grid(row=0, column=0)


        self.btn_prev = ttk.Button(self.bar, text='<', command=self.prev_page)
        self.btn_prev.pack(fill=tk.X, side=tk.LEFT)

        self.btn_next = ttk.Button(self.bar, text='>', command=self.next_page)
        self.btn_next.pack(fill=tk.X, side=tk.LEFT)

        self.img_dirname_label = ttk.Label(self.bar, text='Save Dir:')
        self.img_dirname_label.pack(fill=tk.X, side=tk.LEFT)

        self.img_dirname = tk.StringVar()
        self.img_dirname.set(os.getcwd())
        self.img_dirname_entry = ttk.Entry(self.bar, textvariable=self.img_dirname)
        self.img_dirname_entry.pack(fill=tk.X, side=tk.LEFT)

        self.img_dirname_btn = ttk.Button(self.bar, text='...', command=self.display_path_dialog)
        self.img_dirname_btn.pack(fill=tk.X, side=tk.LEFT)

        self.img_basename_label = ttk.Label(self.bar, text='Image Filename:')
        self.img_basename_label.pack(fill=tk.X, side=tk.LEFT)

        self.img_filename = tk.StringVar()
        self.img_filename.set("img01.jpg")
        self.img_basename = ttk.Entry(self.bar, textvariable=self.img_filename)
        self.img_basename.pack(fill=tk.X, side=tk.LEFT)

        self.save_btn = ttk.Button(self.bar, text="Save Image", command=self.get_subimage,
                                  state=tk.DISABLED)
        self.save_btn.pack(fill=tk.X, side=tk.LEFT, expand=1)

        # self.progress_bar = ttk.Progressbar(self.bar, orient='horizontal', mode='determinate')
        # self.progress_bar.grid(row=0, column=8)
        # self.progress_bar.grid_forget()

        # Make the main Canvas, where most everything is drawn
        self.canvas = tk.Canvas(self, width=width, height=height,
                                cursor='cross')
        self.canvas.pack()#grid(row=1, column=0)
        self.canvas.update()


        # Set up selection rectangle functionality
        self.canvas.bind("<Button-1>", self.selectbox_create)
        self.canvas.bind("<B1-Motion>", self.selectbox_update)
        self.canvas.bind("<Button-3>", self.get_subimage)
        self.canvas.bind("<Configure>", self.on_resize)

    def debug_print(self, event=None):
        print('hello world')

    def display_path_dialog(self):
        dir_name = filedialog.askdirectory(title="Select a Save Directory")
        self.img_dirname.set(dir_name)

    def on_resize(self, event):
        self.images.set_scale(event.height)
        self.show_img()
        self.bar.update()

    def selectbox_delete(self):
        if self.selectbox:
            self.canvas.delete(self.selectbox)
        self.selectbox = 0


    def selectbox_create(self, event):
        self.selectbox.new(event.x, event.y)
        self.save_btn.config(state=tk.DISABLED)

    def selectbox_update(self, event):
        self.selectbox.update(event.x, event.y)
        self.save_btn.config(state=tk.NORMAL)

    def show_img(self):
        """Displays a rescaled page to fit the canvas size."""
        self.selectbox.delete()
        img = self.images.get_scaled_img()

        #tkinter gotcha--must save photoimage as attribute, or it garbage collects it.
        self._photoimg = ImageTk.PhotoImage(image=img)

        self.canvas.create_image(0, 0, image=self._photoimg, anchor='nw')

    def get_subimage(self, event=None):
        coords = self.selectbox.coords
        if not coords:
            messagebox.showerror(parent=self, title="Image Not Selected",
                                 message="Please first click and drag image you wish saved.")
            return

        img = self.images.get_subimage(*coords)
        save_filename = path.join(self.img_dirname.get(), self.img_basename.get())

        # Check if path exists
        if not path.exists(path.dirname(save_filename)):
            messagebox.showerror(parent=self, title="Directory Not Found",
                                 message="Save Directory Not Found.  Please Select an Existing Directory to Continue.")
            self.display_path_dialog()
            return

        # Check if save will overwrite previous file.
        if path.exists(save_filename):
            resp = messagebox.askyesno(parent=self,
                                       title="Overwrite File",
                                       message="This will overwrite file {}.  Are you sure you want to continue?".format(self.img_filename.get()))
            if not resp:
                return
        img.save(save_filename)


        # Increment Filename index
        new_save_filename = io.replace_filename_index(self.img_filename.get())
        self.img_filename.set(new_save_filename)


    def next_page(self):
        self.images.next_page()
        self.show_img()
        self.save_btn.config(state=tk.DISABLED)

    def prev_page(self):
        self.images.prev_page()
        self.show_img()
        self.save_btn.config(state=tk.DISABLED)


