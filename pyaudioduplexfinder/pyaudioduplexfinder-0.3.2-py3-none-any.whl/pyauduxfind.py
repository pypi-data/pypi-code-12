from pyaudioduplexfinder.pyaudioduplexfinder import PyAudioDupleyFinder


import click

@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--analyze', is_flag=True)
@click.argument('pathname', type=click.Path(exists=True))
@click.option('--hash-type', type=click.Choice(['md5', 'sha1', 'sha256', 'sha512']), default='sha256')
@click.option('--saveresult/--no-saveresult', default=True)
def cli(debug, analyze, pathname,  hash_type, saveresult):
    click.clear()
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))
    pyaudufind = PyAudioDupleyFinder(pathname, ('.mp3', '.wav'))
    if analyze:
        pyaudufind.analyze(hash_type, debug)
        duplfile = pyaudufind.get_duplicate_list()
        pyaudufind.print_duplicate_list(duplfile)
        if saveresult:
            pyaudufind.save_duplicates_to_yaml(duplfile)
    else:
        pyaudufind.print_file_list()

