class PageCollection:

    def __init__(self, images):
        self.images = images
        self.__page_idx = 0
        self.display_scale = 1.

    def next_page(self):
        self.page_idx += 1

    def prev_page(self):
        self.page_idx -= 1

    @property
    def page_idx(self):
        return self.__page_idx

    @page_idx.setter
    def page_idx(self, value):
        self.__page_idx = max(0, min(value, len(self.images)-1))

    def get_current_image(self):
        return self.images[self.page_idx]

    def set_scale(self, height):
        self.display_scale = height / self.get_current_image().size[1]

    def get_scaled_img(self):
        """Displays a rescaled page to fit the canvas size."""
        img = self.get_current_image()
        width = int(img.size[0] * self.display_scale)
        height = int(img.size[1] * self.display_scale)

        img_scaled = img.resize((width, height))
        return img_scaled

    def get_subimage(self, x0, y0, x1, y1):

        rect = [x0, y0, x1, y1]
        rect = [int(coord / self.display_scale) for coord in rect]
        subimg = self.get_current_image().crop(rect)
        return subimg