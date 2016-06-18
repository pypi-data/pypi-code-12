import munch
import logging
import io
import yaml
import os

log = logging.getLogger(__name__)


def load(filename):
    """
    Load a Project From a File

    Foo bar

    :param filename: The fully qualified Path and Filename to Load
    :return:
    """
    #   check if the project file exists
    logging.debug("looking for project config file [{0}]".format(filename))
    if not os.path.exists(filename):
        log.debug("could not locate the project configuration file")
        raise Exception("uModules Project Configuration File [{0}] was not Found.".format(filename))

    #   open the file
    file = io.open(filename)

    #   convert contents to yaml
    contents = yaml.load(file.read())

    #   munch the project
    project = __munch_project(contents)

    #   replace tokens
    project = __replace_tokens(project)

    #   validate the project
    if not __validate_project(project):
        raise Exception("Problem Detected with Project Configuration File")

    #   return the project
    return project


def __munch_project(contents):
    return munch.Munch(contents)


def __replace_tokens(project):
    return project


def __validate_project(project):

    #   error!
    if not hasattr(project, "name") and not hasattr(project, "project"):
        log.error("project configuration is missing [name] or [project] attribute")
        return False

    #   error!
    if not hasattr(project, "unity_path"):
        log.error("project configuration is missing [unity_path] attribute")
        return False

    #   error!
    if not os.path.exists(project.unity_path):
        log.error("[unity_path] is not valid")
        return False

    #   error!
    if not hasattr(project, "unity_packages_path"):
        log.error("project configuration is missing [unity_packages_path] attribute")
        return False

    #   error!
    if not os.path.exists(project.unity_packages_path):
        log.error("[unity_packages_path] is not valid")
        return False

    #   if name is missing use project
    if not hasattr(project, "name"):
        project.name = project.project

    #   when project is missing use the name (backwards compatibility)
    if not hasattr(project, "project"):
        project.project = project.name

    #   default type
    if not hasattr(project, 'default_type'):
        project.default_type = "git"

    return True

