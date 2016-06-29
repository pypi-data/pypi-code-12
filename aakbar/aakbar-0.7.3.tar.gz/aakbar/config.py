# -*- coding: utf-8 -*-
'''Implements commands related to configuration parameters
'''

# module imports
from . import cli, get_user_context_obj, logger
from .common import *

# private context function
_ctx = click.get_current_context

@cli.command()
def show_config():
    '''Print location and contents of config file.

        Example:
            aakbar -v show_config
    '''
    global  config_obj

    if config_obj.config_dict == {}:
        logger.info('No configuration file was found.')
    else:
        logger.info('Configuration file path is "%s".', config_obj.path)
        for key in config_obj.config_dict.keys():
            logger.info('  %s: %s', key, config_obj.config_dict[key])


@cli.command()
@click.option('-f', '--force', is_flag=True, default=False,
              help='Overwrite existing definition.')
@click.argument('identifier', type=str)
@click.argument('dir', type=click.Path(writable=True))
def define_set(identifier, dir, force):
    '''Define an identifier and directory for a set.

    IDENTIFIER:
        a short code by which this data set will be known.
    DIR:
        absolute or relative path to files.  Must be writable.

    Example::
        aakbar define_set glymax ./Glycine_max

    '''
    global config_obj
    if identifier in config_obj.config_dict['sets'] and not force:
        logger.error('Set "%s" is already defined, use "--force" to override.',
                     identifier)
    else:
        path = dir
        if identifier in config_obj.config_dict['sets'] and force:
            logger.info('Overriding existing set "%s" definition.', identifier)
            [config_obj.config_dict['sets'].remove(identifier)
             for i in range(config_obj.config_dict['sets'].count(identifier))]
        config_obj.config_dict['sets'].append(identifier)
        config_obj.config_dict[identifier] = {'dir': str(path), 'label': identifier}
        config_obj.write_config_dict()
        logger.info('Set "%s" will refer to directory "%s".', identifier, dir)


@cli.command()
@click.argument('identifier', type=str)
@click.argument('label', type=str)
def label_set(identifier, label):
    '''Define label associated with a set.
    '''
    global config_obj
    if identifier not in config_obj.config_dict['sets']:
        logger.error('Set "%s" is not defined.', identifier)
        sys.exit(1)
    else:
        config_obj.config_dict[identifier]['label'] = label
        logger.info('Label for %s is now "%s".', identifier, label)
        config_obj.write_config_dict()


@cli.command()
@click.argument('plot_type', type=str, nargs=-1)
def set_plot_type(plot_type):
    '''Define label associated with a set.
    '''
    global config_obj
    plot_types = ['svg', 'jpg', 'ps', 'pdf', 'svgr', 'png', 'tiff', 'eps']
    if len(plot_type) == 0:
        logger.info('Supported plot types are:')
        for typename in plot_types:
            logger.info('   %s', typename)
    elif len(plot_type) > 1:
        logger.error('Only one argument for set_plot_type is allowed.')
        sys.exit(1)
    elif plot_type[0] not in plot_types:
        logger.error('Plot type "%s" is not defined.', plot_type[0])
        logger.info('Supported plot types are:')
        for typename in plot_types:
            logger.info('   %s', typename)
        sys.exit(1)
    else:
        config_obj.config_dict['plot_type'] = plot_type[0]
        logger.info('Plot type is now %s.', plot_type[0])
        config_obj.write_config_dict()


@cli.command()
@click.argument('dir', type=click.Path(writable=True))
@click.argument('label', type=str)
def define_summary(dir, label):
    '''Define summary directory and label.
    '''
    global config_obj
    path = str(Path(dir).expanduser())
    logger.info('Summary output will go in directory "%s".', path)
    config_obj.config_dict['summary']['dir'] = path
    config_obj.config_dict['summary']['label'] = label
    config_obj.write_config_dict()


@cli.command()
@click.argument('dir', type=str, default='')
def init_config_file(dir):
    '''Initialize a configuration file.

    :param dir: Optional directory in which to initialize the file.
    If not present, the system-dependent default application directory
    will be used.  If this argument is '.', then the current working
    directory will be used.  This argument accepts tilde expansions.
    '''
    global config_obj
    config_obj.write_config_dict(dir=dir, config_dict={})


@cli.command()
@click.argument('name', type=str, nargs=-1)
def set_simplicity_object(name):
    '''Select simplicity-calculation object.

    :param name: Name object of a SimplicityObject of global scope.
    :return:
    '''
    global config_obj
    known_simplicity_objects = _ctx().obj['simplicity_objects']
    if len(name) == 0:
        print('        Name       Description')
        for obj in known_simplicity_objects:
            print('%s: %s' %('{:>12}'.format(obj.label), obj.desc))
        try:
            current_simplicity_object = config_obj.config_dict['simplicity_object_label']
        except KeyError:
            current_simplicity_object = 'undefined'
        print('Current simplicity object is %s.'%current_simplicity_object)
    elif len(name) > 1:
        logger.error('Only one function may be specified')
        sys.exit(1)
    else:
        for obj in known_simplicity_objects:
            if obj.label == name[0]:
                logger.info('simplicity function is now %s.', name[0])
                config_obj.config_dict['simplicity_object_label'] = name[0]
                config_obj.write_config_dict()
                return
        logger.error('Function "%s" is not a known simplicity function.', name[0])
        sys.exit(1)

