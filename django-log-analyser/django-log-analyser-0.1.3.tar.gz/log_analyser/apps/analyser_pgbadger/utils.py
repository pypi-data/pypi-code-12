import subprocess


def create_pgbadger_report_from_log(log_file_path):
    report_path = log_file_path + '.html'
    cmd = "pgbadger -p '%t:%r:%u@%d:[%p]:' -o {0} {1}".format(report_path, log_file_path)

    # TODO: Handle exceptions
    # TODO: Do not use shell=True
    subprocess.call(cmd, shell=True)
    return report_path
