#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# sentiment_tweets                                                             #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program collates tweets and calculates the sentiment of the tweets. It  #
# then presents the results in a table.                                        #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help               display help message
    --version                display version and exit
    -v, --verbose            verbose logging
    -s, --silent             silent
    -u, --username=USERNAME  username
"""

name    = "sentiment_tweets"
version = "2016-06-22T1725Z"
logo    = None

import docopt

import abstraction
import propyte
import pyprel

def main(options):

    global program
    program = propyte.Program(
        options = options,
        name    = name,
        version = version,
        logo    = logo
    )
    global log
    from propyte import log

    log.info("")

    usernames = [
        "AndrewYNg",
        "geoff_hinton",
        "SamHarrisOrg",
        "ylecun"
    ]

    tweets = abstraction.access_users_tweets(
        usernames = usernames
    )

    log.info("\ntable of tweets:\n")

    print(tweets.table())

    log.info("\nmost frequently expressed calculated sentiments of users:\n")

    users_sentiments_single_most_frequent = tweets.users_sentiments_single_most_frequent()

    pyprel.print_dictionary(dictionary = users_sentiments_single_most_frequent)

    users_sentiment_negative = []
    for username, sentiment in users_sentiments_single_most_frequent.iteritems():
        if sentiment == "neg":
            users_sentiment_negative.append(username)
    log.info("list of users expressing negative sentiments most frequently:\n\n{usernames}".format(
        usernames = users_sentiment_negative
    ))

    log.info("")

    program.terminate()

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
