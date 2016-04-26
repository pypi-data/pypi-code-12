from pyaudioduplexfinder.pyaudioduplexfinder import PyAudioDupleyFinder

import click, pyprind, humanfriendly


@click.command()
@click.option('--debug/--no-debug', default=False)
@click.option('--analyze', is_flag=True)
@click.argument('pathname', type=click.Path(exists=True))
@click.option('--hash-type', type=click.Choice(['md5', 'sha1', 'sha256', 'sha512']), default='sha256')
@click.option('--saveresult/--no-saveresult', default=True)
@click.option('--min-filesize', type=click.INT, default=2000000)
def cli(debug, analyze, pathname,  hash_type, saveresult, min_filesize):
    click.clear()
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))
    pyaudufind = PyAudioDupleyFinder(pathname)
    file_list = pyaudufind.create_file_list(pathname, ('.mp3', '.wav'), min_filesize, debug)
    if analyze:
        bar = pyprind.ProgBar(len(file_list), monitor=True, width=100)
        pyaudufind.analyze(hash_type, debug, bar)
        click.clear()
        print(str(bar) + '\n')
        duplfile = pyaudufind.get_duplicate_list()
        for dup in duplfile:
            print("%s %s" % (humanfriendly.format_size(dup.get_size_recovery()), dup.file_hash))
            for d in dup.files:
                print("\t- %s" % d)
            print()
        print()
        if saveresult:
            pyaudufind.save_duplicates_to_yaml(duplfile)
    else:
        if debug:
            for i in file_list:
                click.echo(click.style(i._str, fg='yellow', dim=True))
        click.echo(click.style('File count ' + str(len(file_list)), fg='green'), nl=True)




