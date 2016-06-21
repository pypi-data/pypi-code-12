# coding=utf-8
"""
Show connection variables from curl

Usage:
  httpdebug.py [options] <url>

Options:
  -h --help         Show this screen.
  --outfile=<data>  File for received data [default: /dev/null].

author  : rabshakeh (erik@a8.nl)
project : httpdebug
created : 19-05-15 / 16:41
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from arguments import Arguments
from cmdssh import call_command
from consoleprinter import *


def main():
    """
    main
    """
    arguments = Arguments(__doc__)

    # noinspection PyUnresolvedReferences
    command = "/usr/bin/curl -s -vv -o {}  {} -w ".format(arguments.outfile, arguments.url)
    command += """
"         content_type:  %{content_type}
    filename_effective:  %{filename_effective}
          p_entry_path:  %{ftp_entry_path}
             http_code:  %{http_code}
          http_connect:  %{http_connect}
              local_ip:  %{local_ip}
            local_port:  %{local_port}
          num_connects:  %{num_connects}
         num_redirects:  %{num_redirects}
          redirect_url:  %{redirect_url}
             remote_ip:  %{remote_ip}
           remote_port:  %{remote_port}
         size_download:  %{size_download}
           size_header:  %{size_header}
          size_request:  %{size_request}
           size_upload:  %{size_upload}
        speed_download:  %{speed_download}
          speed_upload:  %{speed_upload}
     ssl_verify_result:  %{ssl_verify_result}
       time_appconnect:  %{time_appconnect}
          time_connect:  %{time_connect}
       time_namelookup:  %{time_namelookup}
      time_pretransfer:  %{time_pretransfer}
         time_redirect:  %{time_redirect}
    time_starttransfer:  %{time_starttransfer}
            time_total:  %{time_total}
         url_effective:  %{url_effective}
                    ----------

            time_total:  %{time_total}\n@@"; """.strip()

    result = call_command(command, streamoutput=False, returnoutput=True, ret_and_code=True)

    if result[0] == 0:
        print("")
        print("> Downloading\033[91m", arguments.url ,"\033[0mto\033[32m", arguments.outfile, "\033[0m")
        print("")
        print("\033[37m"+ result[1].split("@@")[1], "\033[0m\n")
        print(colorize_for_print(remove_extra_indentation(result[1].split("@@")[0], padding=1, frontspacer="@$").replace("@$", " ")))
        print("")
    else:
        print("error", result[0])
        print(result[1])
        print("")
        print(command)
if __name__ == "__main__":
    main()
