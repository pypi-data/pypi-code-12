import os

RESET  = "$(tput sgr0)"
BACKSPACE = "%x08"


class YologGenerator(object):
    BLACK  = "$(tput bold)$(tput setaf 0)"
    RED    = "$(tput bold)$(tput setaf 1)"
    GREEN  = "$(tput bold)$(tput setaf 2)"
    YELLOW = "$(tput bold)$(tput setaf 3)"
    BLUE   = "$(tput bold)$(tput setaf 4)"
    PURPLE = "$(tput bold)$(tput setaf 5)"
    CYAN   = "$(tput bold)$(tput setaf 6)"
    WHITE  = "$(tput setaf 7)"

    def __init__(self):
        self._hash_color = "YELLOW"
        self._hash = "{0}%h{1}".format(
            getattr(self, self._hash_color), RESET)

        self._author_color = "BLUE"
        self._author = "{0}%an{1}".format(
            getattr(self, self._author_color), RESET)

        self._date_color = "GREEN"
        self._date = "{0}%aD{1}{2}".format(
            getattr(self, self._date_color), BACKSPACE * 15, RESET)

        self._refs_color = "RED"
        self._refs = "{0}%d{1}".format(
            getattr(self, self._refs_color), RESET)

        self._description_color = "WHITE"
        self._description = "{0}%s{1}".format(
            getattr(self, self._description_color), RESET)

        self._format = "{0}~~~{1}~~~{2}~~~{3} {4}".format(
            self._hash, self._author, self._date, self._refs, self._description
        )

    # All the getters return the color of their respective parameter, as the
    # formatted string is interpreted by git and is hardly readable to user.
    def get_hash_color(self):
        return self._hash_color

    def set_hash_color(self, color):
        self._hash_color = color.upper()

    def get_author_color(self):
        return self._author_color

    def set_author_color(self, color):
        self._author_color = color.upper()

    def get_date_color(self):
        return self._date_color

    def set_date_color(self, color):
        self._date_color = color.upper()

    def get_refs_color(self):
        return self._refs_color

    def set_refs_color(self, color):
        self._refs_color = color.upper()

    def get_description_color(self):
        return self._description_color

    def set_description_color(self, color):
        self._description_color = color.upper()

    # Make properties out of these getter setters.
    hash_color = property(get_hash_color, set_hash_color)
    author_color = property(get_author_color, set_author_color)
    date_color = property(get_date_color, set_date_color)
    refs_color = property(get_refs_color, set_refs_color)
    description_color = property(get_description_color, set_description_color)

    def set_gitconfig_alias(self):
        os.system(
            "git config --global alias.yolog "
            "'!git log --pretty=\"tformat:{0}\" --graph --all $* | "
            "column -t -s \"~~~\" | less -FXRS'".format(self._format))


if __name__ == "__main__":
    yologgen = YologGenerator()
    yologgen.set_gitconfig_alias()
