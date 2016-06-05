
import io
import logging
import os.path
import shutil
import subprocess
import sys
import tarfile
import lzma

import wayround_org.utils.exec
import wayround_org.utils.file
import wayround_org.utils.path
import wayround_org.utils.stream


CANONICAL_COMPRESSORS = frozenset(['xz', 'lzma', 'bzip2', 'gzip'])


def _extract_zip(file_name, output_dir):

    ret = 0

    try:
        proc = wayround_org.utils.exec.simple_exec(
            'unzip', stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=sys.stderr,
            options=['-qq', '-o', file_name, '-d', output_dir],
            )
    except:
        logging.exception("unzip start error")
        ret = 1
    else:
        ret = proc.wait()

    return ret


def _extract_7z(file_name, output_dir):

    ret = 0

    try:
        proc = wayround_org.utils.exec.simple_exec(
            '7z', stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=sys.stderr,
            options=['x', '-y', '-o{}'.format(output_dir), file_name],
            )
    except:
        logging.exception("unzip start error")
        ret = 1
    else:
        ret = proc.wait()

    return ret


def _extract_tar_7z(file_name, output_dir):

    ret = 0

    try:
        proc_7z = wayround_org.utils.exec.simple_exec(
            '7z',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,
            options=['x', '-so', file_name],
            )
    except:
        logging.exception("7z start error")
        ret = 1

    else:

        try:
            proc_tar = wayround_org.utils.exec.simple_exec(
                'tar',
                stdin=proc_7z.stdout,
                stdout=subprocess.PIPE,
                stderr=None,
                options=[
                    '--no-same-owner',
                    '--no-same-permissions',
                    '-xlRC',
                    output_dir
                    ]
                )
            proc_7z.wait()
        except:
            logging.exception("tar start error")
            ret = 2
        else:
            proc_tar.wait()

        finally:
            if proc_tar.returncode is None:
                proc_tar.terminate()

    return ret


def _extract_tar_arch(file_name, output_dir, compressor, log=None):

    # TODO: cleanups and reworks required

    os.makedirs(output_dir, exist_ok=True)

    out = None
    err = None
    if log is not None:
        out = log.stdout
        err = log.stderr

    p = subprocess.Popen(
        ['tar', '-xf', file_name, '-C', output_dir, '-v'],
        stderr=err,
        stdout=out
        )
    ret = p.wait()
    return ret

    '''
    if not compressor in CANONICAL_COMPRESSORS:
        raise ValueError(
            "compressor not in `{}'".format(CANONICAL_COMPRESSORS)
            )

    ret = extract_tar_canonical(
        file_name,
        output_dir,
        compressor,
        verbose_tar=True,
        verbose_compressor=True,
        log=log,
        add_tar_options=[
            '--no-same-owner',
            '--no-same-permissions'
            ]
        )

    return ret
    '''


def extract(file_name, output_dir, log=None):

    ret = None

    if file_name.endswith('.tar.lzma'):
        ret = _extract_tar_arch(file_name, output_dir, 'lzma', log=log)

    elif file_name.endswith('.tar.bz2'):
        ret = _extract_tar_arch(file_name, output_dir, 'bzip2', log=log)

    elif file_name.endswith('.tar.gz'):
        ret = _extract_tar_arch(file_name, output_dir, 'gzip', log=log)

    elif file_name.endswith('.tar.xz'):
        ret = _extract_tar_arch(file_name, output_dir, 'xz', log=log)

    elif file_name.endswith('.tar.7z'):
        ret = _extract_tar_7z(file_name, output_dir)

    elif file_name.endswith('.tbz2'):
        ret = _extract_tar_arch(file_name, output_dir, 'bzip2', log=log)

    elif file_name.endswith('.tgz'):
        ret = _extract_tar_arch(file_name, output_dir, 'gzip', log=log)

    elif file_name.endswith('.zip'):
        ret = _extract_zip(file_name, output_dir)

    elif file_name.endswith('.7z'):
        ret = _extract_7z(file_name, output_dir)

    else:
        logging.error("Unsupported extension")

    if ret is None:
        raise Exception("Not implemented")

    return ret


def determine_compressor_by_filename(file_name, mute=False):

    ret = None

    if file_name.endswith('.lzma'):
        ret = 'xz'

    elif file_name.endswith('.bz2'):
        ret = 'bzip2'

    elif file_name.endswith('.gz'):
        ret = 'gzip'

    elif file_name.endswith('.xz'):
        ret = 'xz'

    else:
        if not mute:
            logging.error("Unknown compressor {}".format(file_name))

    return ret


def determine_extension_by_filename(file_name, mute=False):

    ret = None

    for i in ['.lzma', '.bz2', '.gz', '.xz']:

        if file_name.endswith(i):
            ret = i
            break

    if not ret:
        if not mute:
            logging.error("Unknown compressor extension {}".format(file_name))

    return ret


def canonical_compressor(
        compressor,
        stdin=None,
        stdout=None,
        stderr=None,
        options=None,
        ):
    """
    Canonical compressor shortcut

    Works only with `{}' compressors which
    must support -0 .. -9 , -v and -d options in canonical way
    """.format(repr(list(CANONICAL_COMPRESSORS)))

    # print("canonical_compressor: {}".format())

    if options is None:
        options = []

    if not compressor in CANONICAL_COMPRESSORS:
        raise ValueError(
            "canonical_compressor supports only"
            " `{}', but `{}' requested".format(
                list(CANONICAL_COMPRESSORS),
                compressor
                )
            )

    '''
    c = subprocess.Popen(
        [compressor] + options,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr
        )

    ret = c.wait()
    '''
    # while True:

    #'''
    ret = wayround_org.utils.exec.process_stream(
        compressor,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        options=options
        )
    #'''

    return ret


def archive_tar_canonical(
        dirname, output_filename,
        compressor,
        verbose_tar=False,
        verbose_compressor=False,
        bufsize=(2 * 1024 ** 2),
        additional_tar_options=None
        ):

    ret = 0
    try:
        fobj = open(output_filename, 'wb')
    except:
        logging.exception("Error opening file for write")
        ret = 1
    else:
        try:
            ret = archive_tar_canonical_fobj(
                dirname,
                fobj,
                compressor,
                verbose_tar,
                verbose_compressor,
                bufsize=bufsize,
                additional_tar_options=additional_tar_options
                )
        except:
            logging.exception("Error")
            ret = 2
    finally:
        fobj.close()

    return ret


def archive_tar_canonical_fobj(
        dirname,
        output_fobj,
        compressor,
        verbose_tar=False,
        verbose_compressor=False,
        bufsize=(2 * 1024 ** 2),
        additional_tar_options=None
        ):

    if additional_tar_options is None:
        additional_tar_options = []

    ret = 0

    dirname = wayround_org.utils.path.abspath(dirname)

    if not os.path.isdir(dirname):
        logging.error("Not a directory: {}".format(dirname))
        ret = 1
    else:

        options = []
        stderr = None

        if verbose_tar:
            options += ['-v']
            stderr = sys.stderr

        options += ['-c', '.']

        options += additional_tar_options

        try:
            tarproc = wayround_org.utils.exec.simple_exec(
                'tar',
                options=options,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                cwd=dirname,
                bufsize=bufsize,
                stderr=stderr
                )
        except:
            logging.exception("tar start error")
            ret = 2
        else:

            try:
                options = []
                stderr = None

                if verbose_compressor:
                    options += ['-v']
                    stderr = sys.stderr

                options += ['-9']

                if canonical_compressor(
                        compressor,
                        options=options,
                        stdin=tarproc.stdout,
                        stdout=output_fobj,
                        stderr=stderr
                        ) != 0:
                    ret = 3
                tarproc.wait()
            except:
                logging.exception("Error")

        finally:
            tarproc.poll()
            if tarproc.returncode is None:
                tarproc.terminate()

    return ret


def extract_tar_canonical(
        input_filename,
        dirname,
        compressor,
        verbose_tar=False,
        verbose_compressor=False,
        add_tar_options=None,
        log=None
        ):

    if not compressor in CANONICAL_COMPRESSORS:
        raise ValueError(
            "compressor not in `{}'".format(CANONICAL_COMPRESSORS)
            )

    if add_tar_options is None:
        add_tar_options = []

    ret = 0
    try:
        fobj = open(input_filename, 'rb')
    except:
        logging.exception("Error opening file for read")
        ret = 1
    else:
        try:
            ret = extract_tar_canonical_fobj(
                fobj,
                dirname,
                compressor,
                verbose_tar,
                verbose_compressor,
                add_tar_options,
                log=log
                )
        finally:
            fobj.close()
    return ret


def extract_tar_canonical_fobj(
        input_fobj,
        dirname,
        compressor,
        verbose_tar=False,
        verbose_compressor=False,
        add_tar_options=[],
        log=None
        ):

    if not compressor in CANONICAL_COMPRESSORS:
        raise ValueError(
            "compressor not in `{}'".format(CANONICAL_COMPRESSORS)
            )

    if add_tar_options is None:
        add_tar_options = []

    dirname = wayround_org.utils.path.abspath(dirname)

    ret = wayround_org.utils.file.create_if_not_exists_dir(dirname)

    if ret != 0:
        logging.error(
            "Error while checking destination dir: {}".format(dirname)
            )
        ret = 1
    else:

        options = [] + add_tar_options

        if verbose_tar:
            options += ['-v']

        options += ['-x']

        tarproc = None
        try:
            sout = sys.stdout

            if log is not None:
                # if False:
                sout = log.stdout
            tarproc = wayround_org.utils.exec.simple_exec(
                "tar",
                options=options,
                stdin=subprocess.PIPE,
                stdout=sout,
                cwd=dirname,
                stderr=sout
                )
        except:
            logging.exception("tar error detected")
            ret = 2
        else:

            try:
                options = []

                if verbose_compressor:
                    options += ['-v']

                options += ['-d']

                if canonical_compressor(
                        compressor,
                        stdin=input_fobj,
                        stdout=tarproc.stdin,
                        options=options,
                        stderr=sys.stderr
                        ) != 0:

                    ret = 3

                # if log is not None:
                # if False:
                #    log.input_from_Popen_process(tarproc)

                ret = tarproc.wait()

            finally:
                if tarproc.returncode is None:
                    tarproc.terminate()

    return ret


def pack_dir_contents_tar(
        dirname,
        output_filename,
        verbose_tar=False
        ):

    ret = 0

    dirname = wayround_org.utils.path.abspath(dirname)

    if not os.path.isdir(dirname):
        logging.error("Not a directory: {}".format(dirname))
        ret = 1
    else:
        try:
            outf = open(output_filename, 'wb')
        except:
            logging.exception(
                "Coundn't open `{}' for write".format(output_filename)
                )
            ret = 2
        else:

            try:
                options = []
                stderr = subprocess.PIPE

                if verbose_tar:
                    options += ['-v']
                    stderr = sys.stderr

                options += ['-c', '.']

                tarproc = wayround_org.utils.exec.simple_exec(
                    "tar",
                    options=options,
                    stdin=None,
                    stdout=outf,
                    cwd=dirname,
                    bufsize=2 * 1024 ** 2,
                    stderr=stderr
                    )

                tarproc.wait()
            finally:
                outf.close()
    return ret


def tar_get_member(tarobject, cont_name):
    ret = None

    try:
        ret = tarobject.getmember(cont_name)
    except KeyError:
        logging.error("Can't get tar member: {}".format(cont_name))
        ret = 2
    except:
        logging.exception("Can't get tar member: {}".format(cont_name))
        ret = 1

    return ret


def tar_member_extract_file(tarobject, member):
    ret = None

    try:
        ret = tarobject.extractfile(member)
    except:
        logging.exception("Can't get tar member")
        ret = 1

    return ret


def tar_member_get_extract_file(tarobject, cont_name):

    ret = None

    member = tar_get_member(tarobject, cont_name)

    if not isinstance(member, tarfile.TarInfo):
        ret = 1
    else:
        fileobj = tar_member_extract_file(tarobject, member)

        if not isinstance(fileobj, tarfile.ExFileObject):
            ret = 2
        else:
            ret = fileobj

    return ret


def tar_member_get_extract_file_to(tarf, cont_name, output_filename):

    ret = 0
    try:
        fd = open(output_filename, 'wb')
    except:
        logging.error("Error creating output file {}".format(output_filename))
        ret = 1
    else:
        try:
            fobj = tar_member_get_extract_file(
                tarf, cont_name
                )
            try:
                if not isinstance(fobj, tarfile.ExFileObject):
                    logging.error(
                        "Error getting {} from tar".format(cont_name)
                        )
                    ret = 2
                else:
                    wayround_org.utils.stream.cat(fobj, fd)
            finally:
                fobj.close()
        finally:
            fd.close()

    return ret


def xzcat(stdin, convert_to_str=None):

    if convert_to_str == True:
        convert_to_str = 'utf-8'
    elif convert_to_str == False:
        convert_to_str = None

    ret = 0

    dec = lzma.LZMADecompressor(memlimit=200 * 1024 ** 2)

    outstr = None
    if not convert_to_str:
        outstr = io.BytesIO()
    else:
        outstr = io.StringIO()

    dec_data = b''

    while True:

        if dec.eof:
            break

        try:
            buff = stdin.read(2 * 1024 ** 2)

            if len(buff) != 0:

                dec_data = dec.decompress(buff)

                if not convert_to_str:
                    outstr.write(dec_data)
                else:
                    outstr.write(str(dec_data, convert_to_str))

        except:
            logging.exception("Exception while decompressing LZMA data")
            ret = 1
            break

    if ret == 0:
        ret = outstr.getvalue()

    outstr.close()

    return ret


def extract_low(
        log,
        tmpdir,
        tarball,
        outdir,
        unwrap_dir=False,
        rename_dir=False,
        more_when_one_extracted_ok=False
        ):

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)

    if log:
        log.info("Extracting {}".format(os.path.basename(tarball)))

    extr_error = extract(
        tarball, tmpdir, log
        )

    ret = extr_error

    if extr_error != 0:
        if log:
            log.error(
                "Extraction error: {}".format(extr_error)
                )
        ret = 3
    else:

        extracted_dir = os.listdir(tmpdir)

        if len(extracted_dir) > 1 and not more_when_one_extracted_ok:
            if log:
                log.error("too many extracted files")
            ret = 4
        else:

            for i in extracted_dir:

                i2 = tmpdir + os.path.sep + i

                if unwrap_dir:

                    i2_files = os.listdir(i2)
                    for i in i2_files:
                        shutil.move(i2 + os.path.sep + i, outdir)
                    shutil.rmtree(i2)

                else:
                    if rename_dir:
                        n = outdir + os.path.sep + str(rename_dir)
                        if log:
                            log.info(
                                "moving extracted {}\n    as `{}'".format(
                                    i2,
                                    n
                                    )
                                )
                        shutil.move(i2, n)
                    else:
                        if log:
                            log.info(
                                "moving extracted {}\n    to `{}'".format(
                                    i2,
                                    outdir
                                    )
                                )

                        if os.path.isfile(i2):
                            new_file_name = os.path.join(
                                outdir,
                                os.path.basename(i2)
                                )

                            if os.path.isfile(new_file_name):
                                os.unlink(new_file_name)

                        shutil.move(i2, outdir)

    return ret


def tarobj_check_member_sum(tarobj, sums, member_name):
    """
    Check tarball member checksum.

    Sums must be supplied with sums parameter, which must be dict of building::

        sums == {'filename':'checksum'}
    """

    ret = True

    fobj = tar_member_get_extract_file(
        tarobj,
        member_name
        )

    if not isinstance(fobj, tarfile.ExFileObject):
        ret = False
    else:

        summ = wayround_org.utils.checksum.make_fileobj_checksum(fobj)

        if summ == sums[member_name]:
            ret = True
        else:
            ret = False

        fobj.close()

    return ret
