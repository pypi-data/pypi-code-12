#   Copyright 2016 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import requests
import sys


__VERSION__ = "0.0.1"


class Pastee(object):
    """A Pastee client."""

    def __init__(self):
        """Setup the Pastee session."""
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        })

    def create(self, content, key=None, lexer="text", ttl=30):
        """Create a Pastee."""
        api_endpoint = "https://pastee.org/submit"
        data = {
            "content": content,
            "lexer": lexer,
            "ttl": int(ttl * 86400)
        }

        if key:
            data["encrypt"] = "checked"
            data["key"] = key

        return self.session.post(api_endpoint, data=data)


def main():
    """Run the app."""
    parser = argparse.ArgumentParser(version=__VERSION__)
    parser.add_argument("-f", "--file", help="upload a file")
    parser.add_argument("-k", "--key", help="encrypt the pastee with a key")
    parser.add_argument("-l", "--lexer", default="text",
                        help="use a particular lexer (default: text)")
    parser.add_argument("-t", "--ttl", default=30,
                        help="days before paste expires (default: 30)")
    parsed_args = parser.parse_args()

    if parsed_args.file:
        with open(parsed_args.file, "r") as open_file:
            content = open_file.read()
    else:
        content = sys.stdin.read()

    paste = Pastee().create(content, key=parsed_args.key,
                            lexer=parsed_args.lexer, ttl=parsed_args.ttl)
    print paste.url


if __name__ == "__main__":
    main()
