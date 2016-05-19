"""
Fix error in Lahman database 'teams' table.

Takes login details form flags or a text file to access the Lahman
Baseball Database and corrects mismatched information in the 2013 and
2014 'teams' entries for the Chicago teams.
"""

import sys
import pymysql
import utils


def main(args=None):
    """Fix errors in Chicago team data.

    The 2014 db may have mismatches between the Cubs and the White Sox.
    This checks for the mismatches in the teams table for 2013 and 2014
    and corrects it if present.

    If not installed and you want to run manually simply remove references
    to login_dict and replace login details where mydb is declared.
    """
    if args is None:
        args = sys.argv[1:]

    login_dict = utils.flags_to_login_details(args)
    ld = login_dict

    mydb = pymysql.connect(ld['host'], ld['username'], ld['password'], ld['db'])
    cursor = mydb.cursor()
    statement = """SELECT franchID, teamID, yearID, name, park, teamIDBR FROM teams
                   WHERE yearID IN (2013, 2014) AND
                   teamID LIKE 'CH%'"""
    cursor.execute(statement)
    results = cursor.fetchall()
    # check for an error
    checks = [x[0] == x[-1] for x in results]
    # either all checks should be fine or should be broken
    assert checks[0] == checks[1] == checks[2] == checks[3]
    match_ups = []
    if checks[0] is False:
        # the problems are the last 8 columns in teams

        statement = "SHOW columns FROM teams"
        cursor.execute(statement)
        query_results = cursor.fetchall()
        columns = [elem[0] for elem in query_results]
        problem_columns = columns[-8:]

        prob_statement = """SELECT yearID, teamID, """
        for field in problem_columns:
            prob_statement += field + ", "
        prob_statement = prob_statement[:-2]
        prob_statement += """ FROM teams WHERE yearID IN (2013, 2014) AND teamID LIKE 'CH%'
                             ORDER BY yearID DESC"""
        # print prob_statement
        cursor.execute(prob_statement)
        bad_data = cursor.fetchall()
        # hmm
        start_end = [[0, 1], [1, 0], [2, 3], [3, 2]]
        for pair in start_end:
            # print pair[0]
            # print bad_data[pair[0]]

            where_equals = list(bad_data[pair[0]][:2])
            # print start
            set_values = list(bad_data[pair[1]][-8:])
            match_ups.append((where_equals, set_values))
        for match in match_ups:
            update_string = """UPDATE teams SET """
            for count, value in enumerate(match[1]):
                update_string += problem_columns[count] + "="
                if isinstance(value, str):
                    update_string += "'" + value + "', "
                else:
                    update_string += str(value) + ", "
            update_string = update_string[:-2]
            update_string += " WHERE yearID = {} and teamID = '{}'".format(match[0][0], match[0][1])
            cursor.execute(update_string)
            mydb.commit()
        print('Chicago data fixed. Clean data is a good thing.')

    else:
        assert checks[0] is True
        print("Chicago 'teams' data from 2013 and 2014 looks fine.")

    cursor.close()
    return

if __name__ == "__main__":
    main()
