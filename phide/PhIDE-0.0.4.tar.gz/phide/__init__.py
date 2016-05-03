import datetime
import os
import json
import yaml

from subprocess import check_output, CalledProcessError


IGNORED = {".", ".."}


def notebook_walker(dir_path):
    for file_name in os.listdir(dir_path):
        first_letter = file_name[0]
        if file_name in IGNORED or first_letter == '.' or first_letter == '_':
            continue

        path = os.path.join(dir_path, file_name)
        if os.path.isdir(path):
            if first_letter != '.' and first_letter != '_':
                yield from notebook_walker(path)
        else:
            if first_letter != '_' and file_name.endswith(".ipynb"):
                yield dir_path, path


def project_walker(base_dir):
    base_dir = os.path.abspath(base_dir)
    for path, name in notebook_walker(base_dir):
        project_path = os.path.abspath(path).replace(base_dir, "")
        yield project_path, name


def get_branch(cwd):
    try:
        branch_list = check_output(["git", "branch"], cwd=cwd)
        for line in branch_list.splitlines():
            if line.startswith(b"* "):
                return line[2:].decode('utf8')
    except CalledProcessError as e:
        return None


def get_commit_hash(cwd):
    line = check_output(["git", "log", "-1", "--oneline"], cwd=cwd)
    return line.decode('utf8').split(" ")[0]


def get_git_info(cwd):
    branch = get_branch(cwd)
    if branch is None:
        return None
    else:
        return branch, get_commit_hash(cwd)


DEFAULTS = {'title': "PhiDE Extract",
            'author': "PhiDE"}


def load_preferences(cwd):
    preferences = {}
    preferences.update(DEFAULTS)

    try:
        with open(os.path.join(cwd, ".phide.json")) as fp:
            preferences.update(json.load(fp))
    except FileNotFoundError:
        pass

    # Special.
    if 'date' not in preferences:
        date_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        git_info = get_git_info(cwd)
        if git_info is not None:
            date_s += " (git:{}:{})".format(*git_info)
        preferences['date'] = date_s

    return preferences


def generate_header(cwd, prefs):
    header = yaml.dump(prefs, explicit_start=True, default_flow_style=False)
    return header + "---\n"


ARTIFACT_ID = 0


def gensym():
    global ARTIFACT_ID
    ARTIFACT_ID += 1
    return ARTIFACT_ID


def serialize(output_dir, extension, data):
    identifier = gensym()
    file_name = os.path.join("media", "{}.{}".format(identifier, extension))
    with open(os.path.join(output_dir, file_name), "w") as fp:
        fp.write("".join(data))
    return file_name, identifier


def process_notebook(notebook_path, output_dir, output_fp):
    with open(notebook_path) as fp:
        notebook = json.load(fp)

    for cell in notebook["cells"]:
        cell_type = cell.get("cell_type")

        # TODO: REFACTOR THIS SLOP.
        if cell_type == "markdown":
            output_fp.write("".join(cell["source"]))
            output_fp.write("\n")
        elif cell_type == "code" and "outputs" in cell:
            outputs = cell["outputs"]
            for output in outputs:
                if output.get("output_type", "") == "display_data":
                    for kind, data in output["data"].items():
                        if kind == "image/svg+xml":
                            path, fig = serialize(output_dir, "svg", data)
                            img = "![Figure {}]({})".format(fig, path)
                            output_fp.write(img + "\n")


def build_html(working_dir, input_file, output_file):
    return check_output(["pandoc",
                         "-s", "-o", output_file, input_file,
                         "--mathjax", "--smart",
                         "--filter", "pandoc-citeproc"],
                        cwd=working_dir)
