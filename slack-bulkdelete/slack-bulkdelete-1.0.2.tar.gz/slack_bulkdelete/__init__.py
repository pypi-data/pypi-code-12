"""
Bulk delete files in Slack that are:
    owned by user <user> (optional--if not specified, everyone) and
    older than <days_old> days and
    bigger than <min_size> and
    not pinned

"""
import argparse
import json
import os

from datetime import datetime, timedelta

import slacker

DEFAULT_DAYS_OLD = 30
DEFAULT_MIN_SIZE = 200
DEFAULT_APITOK_FILE = "~/.slack_api_token"


def get_uid(slack, name):
    """Get the UID based upon the username"""
    uid = slack.users.get_user_id(name)
    if not uid:
        raise ValueError("cannot find user {}".format(name))
    return uid


class UidCache(object):
    """Get (and cache) the username based upon the uid"""
    cache = {}

    def get_name(self, slack, uid):
        """Return username"""
        if uid not in self.cache:
            self.cache[uid] = slack.users.info(uid).body["user"]["name"]
        return self.cache[uid]


def main():
    """Delete Slack files"""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-C", "--config-path", default=DEFAULT_APITOK_FILE,
                        help="configuration info")
    parser.add_argument("-n", "--dry-run", action="store_true", help="just simulate the deletes")
    parser.add_argument("-u", "--user", dest="users", action="append", help="limit delete to user")
    parser.add_argument("-a", "--max-age", type=int, default=DEFAULT_DAYS_OLD,
                        help="maximum age in days")
    parser.add_argument("-s", "--min-size", type=int, default=DEFAULT_MIN_SIZE,
                        help="minimum size (in kb) of file to delete")
    parser.add_argument("-p", "--pinned", action="store_true",
                        help="include pinned files (you don't want this!)")
    args = parser.parse_args()

    with open(os.path.expanduser(args.config_path), "r") as apitok:
        slack = slacker.Slacker(json.load(apitok))

    if args.users is None:
        args.users = ["-all-users-"]

    args.min_size *= 1024

    end_date = (datetime.now() - timedelta(days=args.max_age)).timestamp()
    count = 1
    total = 2
    deleted_size = 0

    umap = UidCache()

    for user in args.users:
        uid = get_uid(slack, user) if user != "-all-users-" else None

        while total > count:
            response = slack.files.list(user=uid, ts_to=end_date)
            paging = response.body["paging"]
            total = int(paging["total"])
            count = int(paging["count"])

            for finfo in response.body["files"]:
                created = int(finfo["created"])
                ctime = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M:%S")
                size = int(finfo["size"])
                pinned = finfo.get("pinned_to")
                creator = umap.get_name(slack, finfo["user"])
                delete = size > args.min_size and (not pinned or args.pinned)

                print("{:9} {} {} ({}/{:.0f}k)".
                      format("Deleting:" if delete else "Saving:",
                             ctime, finfo["name"], creator, size/1024))
                if delete:
                    deleted_size += size
                    if not args.dry_run:
                        slack.files.delete(finfo["id"])

                if created < int(end_date):
                    end_date = str(created - 1)

    print("Total size of files deleted: {:.2f}mb".format(deleted_size / (1024*1024)))


if __name__ == "__main__":
    main()
