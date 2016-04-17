# This file is part of govtrack2csv.
#
# govtrack2csv is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with govtrack2csv.  If not, see <http://www.gnu.org/licenses/>

import csv
import json
import logging
import multiprocessing
import os
import os.path
import pandas as pd
import sys
import yaml  # Ruby users should die.

from collections import defaultdict

from govtrack2csv.util import datestring_to_datetime
from govtrack2csv.model import Congress

logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.DEBUG)

LEGISLATOR_DIR = 'congress-legislators'
CONGRESS_DIR = 'congress'


def import_legislators(src):
    """
    Read the legislators from the csv files into a single Dataframe. Intended
    for importing new data.
    """
    logger.info("Importing Legislators From: {0}".format(src))
    current = pd.read_csv("{0}/{1}/legislators-current.csv".format(
        src, LEGISLATOR_DIR))
    historic = pd.read_csv("{0}/{1}/legislators-historic.csv".format(
        src, LEGISLATOR_DIR))
    legislators = current.append(historic)

    return legislators


def save_legislators(legislators, destination):
    """
    Output legislators datafrom to csv.
    """
    logger.info("Saving Legislators To: {0}".format(destination))
    legislators.to_csv("{0}/legislators.csv".format(destination),
                       encoding='utf-8')


def move_legislators(src, dest):
    logger.info("Moving Legislators")
    legislators = import_legislators(src)
    save_legislators(legislators, dest)
    logger.info("Saved {0} Legislators".format(len(legislators)))

#
# Committee Functions
#


def import_committees(src):
    """
    Read the committees from the csv files into a single Dataframe. Intended for importing new data.
    """
    committees = []
    subcommittees = []

    with open("{0}/{1}/committees-current.yaml".format(src, LEGISLATOR_DIR),
              'r') as stream:
        committees += yaml.load(stream)

    with open("{0}/{1}/committees-historical.yaml".format(src, LEGISLATOR_DIR),
              'r') as stream:
        committees += yaml.load(stream)

    # Sub Committees are not Committees
    # And unfortunately the good folk at thomas thought modeling data with duplicate id's was a good idea.
    # you can have two subcommittees with the ID 12. Makes a simple membership map impossible.
    for com in committees:
        com['committee_id'] = com['thomas_id']
        if 'subcommittees' in com:
            # process sub committees into separate DataFrame
            for subcom in com.get('subcommittees'):
                subcom['committee_id'] = com[
                    'thomas_id'
                ]  # we use committee_id so we can easily merge dataframes
                subcom['subcommittee_id'] = "{0}-{1}".format(
                    subcom['committee_id'], subcom['thomas_id'])
                subcommittees.append(subcom)

            del com['subcommittees']

    committees_df = pd.DataFrame(committees)
    subcommittees_df = pd.DataFrame(subcommittees)

    return [committees_df, subcommittees_df]


def save_committees(committees, dest):
    """
    Output legislators datafrom to csv.
    """
    committees.to_csv("{0}/committees.csv".format(dest), encoding='utf-8')


def save_subcommittees(subcommittees, dest):
    """
    Output legislators datafrom to csv.
    """
    subcommittees.to_csv("{0}/subcommittees.csv".format(dest),
                         encoding='utf-8')


def move_committees(src, dest):
    """
    Import stupid yaml files, convert to something useful.
    """
    comm, sub_comm = import_committees(src)
    save_committees(comm, dest)
    save_subcommittees(comm, dest)


def make_congress_dir(congress, dest):
    """
    If the directory for a given congress does not exist. Make it.
    """

    congress_dir = "{0}/{1}".format(dest, congress)
    path = os.path.dirname(congress_dir)
    logger.debug("CSV DIR: {}".format(path))
    if not os.path.exists(congress_dir):
        logger.info("Created: {0}".format(congress_dir))
        os.mkdir(congress_dir)
    return congress_dir


def load_subjects(congresses):
    temp_array = []
    for con in congresses:
        t_con = pd.DataFrame().from_csv("data/csv/{0}/legislation.csv".format(
            con))
        temp_array.append(t_con)
    return pd.concat(temp_array)


def save_congress(congress, dest):
    """
    Takes a congress object with legislation, sponser, cosponsor, commities
    and subjects attributes and saves each item to it's own csv file.
    """
    try:
        logger.debug(congress.name)
        logger.debug(dest)
        congress_dir = make_congress_dir(congress.name, dest)
        congress.legislation.to_csv("{0}/legislation.csv".format(congress_dir),
                                    encoding='utf-8')
        logger.debug(congress_dir)
        congress.sponsors.to_csv("{0}/sponsor_map.csv".format(congress_dir),
                                 encoding='utf-8')
        congress.cosponsors.to_csv(
            "{0}/cosponsor_map.csv".format(congress_dir),
            encoding='utf-8')
        congress.events.to_csv("{0}/events.csv".format(congress_dir),
                               encoding='utf-8')
        congress.committees.to_csv(
            "{0}/committees_map.csv".format(congress_dir),
            encoding='utf-8')
        congress.subjects.to_csv("{0}/subjects_map.csv".format(congress_dir),
                                 encoding='utf-8')
        congress.votes.to_csv("{0}/votes.csv".format(congress_dir),
                              encoding='utf-8')
        congress.votes_people.to_csv(
            "{0}/votes_people.csv".format(congress_dir),
            encoding='utf-8')
        if hasattr(congress, 'amendments'):
            congress.amendments.to_csv(
                "{0}/amendments.csv".format(congress_dir),
                encoding='utf-8')
    except Exception:
        logger.error("############################################shoot me")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(exc_type, fname, exc_tb.tb_lineno)


def import_committee_membership(src):
    with open(
            "{0}/congress-legislators/committee-membership-current.yaml".format(
                src), 'r') as stream:
        c_membership = yaml.load(stream)

    members = []

    for c in c_membership:
        for member in c_membership[c]:
            member['committee_id'] = c
            member['title'] = member.get('title', 'Member')
            member['party_position'] = member['party']
            member['legislator_id'] = int(member['thomas'])
            del (member['party'])
            del (member['thomas'])
            members.append(member)

    return pd.DataFrame(members)


def save_committee_membership(membership, dest):
    membership.to_csv("{0}/csv/membership.csv".format(dest), encoding='utf-8')


def extract_legislation(bill):
    """
    Returns a list of the legislation fields we need for our legislation DataFrame
    :param bill:
    :return list:
    """
    record = []
    record.append(bill.get('congress', None))
    record.append(bill.get('bill_id', None))
    record.append(bill.get('bill_type', None))
    record.append(bill.get('introduced_at', None))
    record.append(bill.get('number', None))
    record.append(bill.get('official_title', None))
    record.append(bill.get('popular_title', None))
    record.append(bill.get('short_title', None))
    record.append(bill.get('status', None))
    record.append(bill.get('status_at', None))
    record.append(bill.get('top_subject', None))
    record.append(bill.get('updated_at', None))

    return record


def extract_sponsor(bill):
    """
    Return a list of the fields we need to map a sponser to a bill
    """
    logger.debug("Extracting Sponsor")
    sponsor_map = []
    sponsor = bill.get('sponsor', None)
    if sponsor:
        sponsor_map.append(sponsor.get('type'))
        sponsor_map.append(sponsor.get('thomas_id'))
        sponsor_map.append(bill.get('bill_id'))
        sponsor_map.append(sponsor.get('district'))
        sponsor_map.append(sponsor.get('state'))
    logger.debug("END Extracting Sponsor")
    return sponsor_map if sponsor_map else None


def extract_cosponsors(bill):
    """
    Return a list of list relating cosponsors to legislation.
    """
    logger.debug("Extracting Cosponsors")
    cosponsor_map = []
    cosponsors = bill.get('cosponsors', [])
    bill_id = bill.get('bill_id', None)

    for co in cosponsors:
        co_list = []
        co_list.append(co.get('thomas_id'))
        co_list.append(bill_id)
        co_list.append(co.get('district'))
        co_list.append(co.get('state'))
        cosponsor_map.append(co_list)

    logger.debug("End Extractioning Cosponsors")

    return cosponsor_map


def extract_subjects(bill):
    """
    Return a list subject for legislation.
    """
    logger.debug("Extracting Subjects")
    subject_map = []
    subjects = bill.get('subjects', [])
    bill_id = bill.get('bill_id', None)
    bill_type = bill.get('bill_type', None)

    for sub in subjects:
        subject_map.append((bill_id, bill_type, sub))

    logger.debug("End Extractioning Subjects")

    return subject_map


def extract_committees(bill):
    """
    Returns committee associations from a bill.
    """
    bill_id = bill.get('bill_id', None)
    logger.debug("Extracting Committees for {0}".format(bill_id))

    committees = bill.get('committees', None)
    committee_map = []

    for c in committees:
        logger.debug("Processing committee {0}".format(c.get('committee_id')))
        c_list = []
        sub = c.get('subcommittee_id')
        if sub:
            logger.debug("is subcommittee")
            c_list.append('subcommittee')  # type
            c_list.append(c.get('subcommittee'))
            sub_id = "{0}-{1}".format(
                c.get('committee_id'), c.get('subcommittee_id'))
            logger.debug("Processing subcommittee {0}".format(sub_id))
            c_list.append(sub_id)
        else:
            c_list.append('committee')
            c_list.append(c.get('committee'))
            c_list.append(c.get('committee_id'))
        c_list.append(bill_id)
        committee_map.append(c_list)
    return committee_map


# Really don't like how this is comming together.....
def extract_events(bill):
    """
    Returns all events from legislation. Thing of this as a log for congress.
    There are alot of events that occur around legislation. For now we are
    going to kepe it simple. Introduction, cosponsor, votes dates
    """
    events = []
    #logger.debug(events)

    bill_id = bill.get('bill_id', None)
    if bill_id:
        for event in bill.get('actions', []):
            e = []
            e.append(bill_id)
            e.append(event.get('acted_at', None))
            e.append(event.get('how', None))
            e.append(event.get('result', None))
            e.append(event.get('roll', None))
            e.append(event.get('status', None))
            e.append(event.get('suspension', False))
            e.append(event.get('text', None))
            e.append(event.get('type', None))
            e.append(event.get('vote_type', None))
            e.append(event.get('where', None))
            e.append(event.get('calander', None))
            e.append(event.get('number', None))
            e.append(event.get('under', None))
            e.append(event.get('committee', None))
            e.append(event.get('committees', []))
            events.append(e)
    #logger.debug(events)

    return events


def process_bills(congress):
    logger.debug("Processing bills")

    data = defaultdict(list)

    bills = "{0}/{1}/bills".format(congress['src'], congress['congress'])
    logger.info("Processing Bills for {0}".format(congress['congress']))

    for root, dirs, files in os.walk(bills):
        if "data.json" in files and "text-versions" not in root:
            file_path = "{0}/data.json".format(root)
            logger.debug("Processing {0}".format(file_path))
            bill = json.loads(open(file_path, 'r').read())

            logger.debug("OPENED {}".format(file_path))

            # let's start with just the legislative information
            try:
                record = extract_legislation(bill)
                data['legislation'].append(record)

                sponsor = extract_sponsor(bill)
                data['sponsors'].append(sponsor)

                cosponsor = extract_cosponsors(bill)
                data['cosponsors'].extend(cosponsor)

                subject = extract_subjects(bill)
                data['subjects'].extend(subject)

                committee = extract_committees(bill)
                data['committees'].extend(committee)

                evt = extract_events(bill)
                data['events'].extend(evt)

            except Exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error(exc_type, fname, exc_tb.tb_lineno)

    return data


def process_amendments(congress):
    """
    Traverse amendments for a project
    """
    amend_dir = "{0}/{1}/amendments".format(congress['src'],
                                            congress['congress'])
    logger.info("Processing Amendments for {0}".format(congress['congress']))

    amendments = []

    for root, dirs, files in os.walk(amend_dir):
        if "data.json" in files and "text-versions" not in root:
            file_path = "{0}/data.json".format(root)
            logger.debug("Processing {0}".format(file_path))
            a = json.loads(open(file_path, 'r').read())
            amendment = []

            amendment.append(a['amendment_id'])
            amendment.append(a['amendment_type'])
            if a['amends_amendment']:
                amendment.append(a['amends_amendment'].get('amendment_id',
                                                           None))
            else:
                amendment.append(None)
            if a['amends_bill']:
                amendment.append(a['amends_bill'].get('bill_id', None))
            else:
                amendment.append(None)
            if a['amends_treaty']:
                amendment.append(a['amends_treaty'].get('treaty_id', None))
            else:
                amendment.append(None)
            amendment.append(a['chamber'])
            amendment.append(a['congress'])
            amendment.append(a['description'])
            amendment.append(a['introduced_at'])
            amendment.append(a['number'])
            amendment.append(a.get('proposed_at', None))
            amendment.append(a['purpose'])
            amendment.append(a['sponsor'].get('thomas_id', None))
            amendment.append(a['sponsor'].get('committee_id', None))
            amendment.append(a['sponsor']['type'])
            amendment.append(a['status'])
            amendment.append(a['updated_at'])

            amendments.append(amendment)

    return amendments if amendments else [[None] * 17]


def process_votes(congress, lis_to_bio):
    vote_dir = "{0}/{1}/votes".format(congress['src'], congress['congress'])
    logger.info("Processing Votes for {0}".format(congress['congress']))

    votes = {}
    vote_data = []
    vote_person = []
    up_down_set = {'bill', 'amendment', 'passage', 'cloture', 'procedural',
                   'passage-suspension', 'nomination'
                   'recommit'}

    for root, dirs, files in os.walk(vote_dir):
        if "data.json" in files:
            file_path = "{0}/data.json".format(root)
            v = json.loads(open(file_path, 'r').read())
            vote = []

            if v['category'] in up_down_set:
                if v.get('bill', None):
                    bill_id = "{type}{number}-{congress}".format(**v['bill'])
                else:
                    bill_id = None

                yes_vote = 'Yea' if 'Yea' in v['votes'].keys() else 'Aye'
                no_vote = 'Nay' if 'Nay' in v['votes'].keys() else 'No'

                stupid_tally_map = {
                    'Yea': 'y',
                    'Aye': 'y',
                    'Nay': 'n',
                    'No': 'n',
                    'Not Voting': 'nv',
                    'Present': 'p'
                }

                vote.append(str(v.get('amendment', None)))
                vote.append(bill_id)
                vote.append(v['category'])
                vote.append(v['congress'])
                vote.append(v['chamber'])
                vote.append(v['date'])
                vote.append(v['number'])
                vote.append(v['requires'])
                vote.append(v['result'])
                vote.append(v.get('result_text', None))
                vote.append(v['session'])
                vote.append(v['type'])
                vote.append(v['updated_at'])
                vote.append(v['vote_id'])

                try:
                    if v['category'] in up_down_set:
                        vote.append(len(v['votes'][yes_vote]))
                        vote.append(len(v['votes'][no_vote]))
                        vote.append(len(v['votes']['Not Voting']))
                        vote.append(len(v['votes']['Present']))
                    else:
                        vote.append(0)
                        vote.append(0)
                        vote.append(0)
                        vote.append(0)

                except KeyError as ke:
                    logger.error("bad vote key: {0}".format(v['vote_id']))
                    logger.errro(ke)
                except:
                    e = sys.exc_info()[0]
                    logger.error(yes_vote)
                    logger.error(no_vote)
                    logger.error(v['chamber'])
                    logger.error(v['votes'].keys())
                    logger.error(v['category'])
                    raise e

                vote_data.append(vote)
                for k, tallies in v['votes'].items():
                    for tally in tallies:
                        try:
                            logger.debug('got to append')
                            # VP vote shows as string ignore for the time being

                            if not isinstance(tally, str):
                                # looks like some senate votes are recorded using the lis_id
                                # normalize to the bioguide_id
                                if tally['id'] in lis_to_bio:
                                    logger.debug(
                                        "Replacing Tally ID {0} with {1}".format(
                                            tally['id'], lis_to_bio[tally[
                                                'id']]))
                                    tally['id'] = lis_to_bio[tally['id']]

                                #if any(legislators.lis_id == tally['id']):
                                #    tally['id'] = legislators[legislators.lis_id == tally['id']]['bioguide_id'].iloc[0]
                                vote_person.append([stupid_tally_map[k], v[
                                    'vote_id'], tally['id'], tally['party'],
                                                    tally['state'], v['date']])
                        except KeyError as ke:
                            logger.error("bad vote key: {0}".format(ke))
                            logger.error(tally['id'])
                            logger.exception(ke)
                        except Exception as e:
                            logger.error(e)
                            logger.error(v['category'])
                            logger.error(v['vote_id'])
                            logger.error("Tally {0}".format(tally))
                            logger.error(type(tally))
                            logger.error(k)
                            logger.error(tally)
                            raise e

    votes['votes'] = vote_data if vote_data else [[None] * 18]
    votes['people'] = vote_person if vote_person else [[None] * 6]

    return votes


def lis_to_bio_map(folder):
    """
    Senators have a lis_id that is used in some places. That's dumb. Build a
    dict from lis_id to bioguide_id which every member of congress has.
    """
    logger.info("Opening legislator csv for lis_dct creation")
    lis_dic = {}
    leg_path = "{0}/legislators.csv".format(folder)
    logger.info(leg_path)
    with open(leg_path, 'r') as csvfile:
        leg_reader = csv.reader(csvfile)
        for row in leg_reader:
            if row[22]:
                lis_dic[row[22]] = row[19]
    return lis_dic


def convert_congress(congress):
    """
    Recurse the passed govtrack congress directory and convert it's contents
    to a set of csv files from the legislation contained therein.
    :return dict: A Dictionary of DataFrames
    """

    logger.info("Begin processing Congress {0}".format(congress['congress']))

    congress_obj = Congress(congress)
    lis_to_bio = lis_to_bio_map(congress['dest'])

    logger.debug("made congress object")
    logger.debug(congress_obj)

    # We construct lists that can be used to construct dataframes.  Adding to
    # dataframes is expensive so we don't do  that.

    bills = process_bills(congress)
    amendments = process_amendments(congress)
    votes = process_votes(congress, lis_to_bio)

    try:

        logger.debug(" ======================  SAVING {}".format(congress))

        congress_obj.legislation = pd.DataFrame(bills['legislation'] if bills[
            'legislation'] else [[None] * 12])
        congress_obj.legislation.columns = [
            'congress', 'bill_id', 'bill_type', 'introduced_at', 'number',
            'official_title', 'popular_title', 'short_title', 'status',
            'status_at', 'top_subject', 'updated_at'
        ]

        f = [s for s in bills['sponsors'] if s]
        sponsors = f if f else [[None] * 5]
        congress_obj.sponsors = pd.DataFrame(sponsors)
        congress_obj.sponsors.columns = [
            'type', 'thomas_id', 'bill_id', 'district', 'state'
        ]

        c = [s for s in bills['cosponsors'] if len(s) > 0]
        cosponsors = c if c else [[None] * 5]
        congress_obj.cosponsors = pd.DataFrame(cosponsors)
        congress_obj.sponsors.columns = [
            'type', 'thomas_id', 'bill_id', 'district', 'state'
        ]

        c = [s for s in bills['committees'] if len(s) > 0]
        committees = c if c else [[None] * 4]
        congress_obj.committees = pd.DataFrame(committees)
        congress_obj.committees.columns = [
            'type', 'name', 'committee_id', 'bill_id'
        ]

        s = [s for s in bills['subjects'] if len(s) > 0]
        subjects = s if s else [[None] * 3]
        congress_obj.subjects = pd.DataFrame(subjects)
        congress_obj.subjects.columns = ['bill_id', 'bill_type', 'subject']

        e = [s for s in bills['events'] if len(s) > 0]
        events = e if e else [[None] * 16]
        congress_obj.events = pd.DataFrame(events)
        congress_obj.events.columns = [
            'bill_id', 'acted_at', 'how', 'result', 'roll', 'status',
            'suspension', 'text', 'type', 'vote_type', 'where', 'calander',
            'number', 'under', 'committee', 'committees'
        ]

        # Amendment data is not avalible for all congresses
        if amendments:
            congress_obj.amendments = pd.DataFrame(amendments)
            congress_obj.amendments.columns = [
                'amendment_id', 'amendment_type', 'amends_amendment',
                'amends_bill', 'amends_treaty', 'chamber', 'congress',
                'description', 'introduced', 'number', 'proposed', 'purpose',
                'sponsor_id', 'committee_id', 'sponsor_type', 'status',
                'updated'
            ]

        congress_obj.votes = pd.DataFrame(votes['votes'])
        congress_obj.votes.columns = ['amendment_id', 'bill_id', 'category',
                                      'congress', 'chamber', 'date', 'number',
                                      'requires', 'result', 'result_text',
                                      'session', 'type', 'updated_at',
                                      'vote_id', 'yes', 'no', 'not_voting',
                                      'present']

        congress_obj.votes_people = pd.DataFrame(votes['people'])
        congress_obj.votes_people.columns = ['vote', 'vote_id', 'bioguide_id',
                                             'party', 'state', 'date']

        save_congress(congress_obj, congress['dest'])

    except Exception as e:
        logger.error(
            "################### ERRROR SAVING ########################")
        logger.error("congress {0}".format(congress))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        raise e
