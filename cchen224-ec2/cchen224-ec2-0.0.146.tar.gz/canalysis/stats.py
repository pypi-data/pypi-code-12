import csv
from datetime import datetime

def filter(fp_in, fp_out):
    with open(fp_in, 'r') as i:
        csvreader = csv.reader(i)
        with open(fp_out, 'w') as o:
            csvwriter = csv.writer(o)
            for row in csvreader:
                if int(row[4]) > 20:
                    csvwriter.writerow(row)


def merge_post(fp_in, fp_out, user_info, **kwargs):
    # user_id, create_at, location_id, latitude, longitude,
    try:
        user_id = kwargs['user_id']
    except KeyError:
        user_id = 0
    try:
        create_at = kwargs['create_at']
    except KeyError:
        create_at = 1
    try:
        location_id = kwargs['location_id']
    except KeyError:
        location_id = 2
    try:
        latitude = kwargs['latitude']
    except KeyError:
        latitude = 3
    try:
        longitude = kwargs['longitude']
    except KeyError:
        longitude = 4

    info = dict()
    with open(user_info, 'r') as i:
        csvreader = csv.reader(i)
        for row in csvreader:
            info[row[0]] = row[2:5]

    post = dict()
    with open(fp_in, 'r') as i:
        csvreader = csv.reader(i)
        for row in csvreader:
            if row[user_id] in info:
                if row[user_id] not in post:
                    post[row[user_id]] = [row[create_at] + '@' +
                                          row[location_id] +
                                          '->' + row[latitude] + ',' + row[longitude]]
                else:
                    post[row[user_id]].append(row[create_at] + '@' +
                                               row[location_id] +
                                               '->' + row[latitude] + ',' + row[longitude])

    with open(fp_out, 'w') as o:
        csvwriter = csv.writer(o)
        for key in info.keys():
            row = [key]
            row.extend(info[key])
            row.append('|'.join(post[key]))
            csvwriter.writerow(row)
# merge_post('/Users/cchen224/Downloads/instagram_stats/locations.csv',
#            '/Users/cchen224/Downloads/instagram_stats/merge_data.csv',
#            '/Users/cchen224/Downloads/instagram_stats/instagram_user_info.csv')


def split_active(fp_in):
    with open(fp_in, 'r') as i:
        csvreader = csv.reader(i)
        for row in csvreader:
            if int(row[3]) > 1200:
                with open(fp_in.split('.')[0] + '_active.csv', 'a') as o:
                    csv.writer(o).writerow(row)
            else:
                with open(fp_in.split('.')[0] + '_regular.csv', 'a') as o:
                    csv.writer(o).writerow(row)
# split_active('/Users/cchen224/Downloads/instagram_stats/merge_data.csv')


def geo_stats(fp_in):
    posts = []
    with open(fp_in, 'r') as i:
        csvreader = csv.reader(i)
        [posts.extend(row[4].split('|')) for row in csvreader]
    geo = [post for post in posts if not post.endswith(',')]
    return len(posts), len(geo), float(len(geo)) / len(posts)
# geo_stats('/Users/cchen224/Downloads/instagram_stats/merge_data.csv')
# geo_stats('/Users/cchen224/Downloads/instagram_stats/merge_data_active.csv')
# geo_stats('/Users/cchen224/Downloads/instagram_stats/merge_data_regular.csv')

from cutils import ProgressBar
def geo_stats_over_time(fp_in, form):
    bar = ProgressBar(total=sum(1 for _ in open(fp_in)))
    out = dict()
    out_g = dict()
    with open(fp_in, 'r') as i:
        csvreader = csv.reader(i)
        for row in csvreader:
            bar.skip_move(p_skip=0.95)
            for post in row[4].split('|'):
                t = datetime.strptime(post.split('@')[0], '%Y-%m-%d %H:%M:%S').strftime(form)
                if t not in out:
                    out[t] = 1
                    out_g[t] = 0
                else:
                    out[t] += 1
                if not post.endswith(','):
                    out_g[t] += 1
        bar.close()
    return out, out_g

def get_stats(overall, geo_coded, outputFile):
    out = dict()
    for key in overall.keys():
        out[key] = [overall[key], geo_coded[key]]
    with open(outputFile, 'a') as o:
        csvwriter = csv.writer(o)
        for key in out.keys():
            writerow = [key]
            writerow.extend(out[key])
            csvwriter.writerow(writerow)
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data.csv', '%Y')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/y_overall_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data.csv', '%m')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/m_overall_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data.csv', '%w')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/w_overall_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data.csv', '%j')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/j_overall_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_active.csv', '%j')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/j_active_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_active.csv', '%m')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/m_active_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_active.csv', '%w')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/w_active_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_active.csv', '%Y')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/y_active_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_regular.csv', '%w')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/w_regular_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_regular.csv', '%j')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/j_regular_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_regular.csv', '%m')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/m_regular_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_regular.csv', '%Y')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/y_regular_stats.csv')

# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_regular.csv', '%H')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/h_regular_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data.csv', '%H')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/h_overall_stats.csv')
# a,b = geo_stats_over_time('/Users/cchen224/Downloads/instagram_stats/merge_data_active.csv', '%H')
# get_stats(a, b, '/Users/cchen224/Downloads/instagram_stats/h_active_stats.csv')


# locations = []
# with open('/Users/cchen224/Downloads/instagram_stats/merge_data.csv', 'r') as i:
#     csvreader = csv.reader(i)
#     for row in csvreader:
#         locations.extend([post.split('@')[1].split('->')[1] for post in row[4].split('|')])
#
# out = dict()
# for location in locations:
#     if location != ',':
#         tokens = location.split(',')
#         latlon = tokens[0] + ',' + tokens[1]
#     if latlon not in out:
#         out[latlon] = ''
# with open('/Users/cchen224/Downloads/instagram_stats/locations.txt', 'w') as o:
#     [o.write(latlon + '\n') for latlon in out.keys()]
#
#

def get_nposts_per_user(fp_in, fp_out):
    with open(fp_in, 'r') as i:
        csvreader = csv.reader(i)
        with open(fp_out, 'w') as o:
            csvwriter = csv.writer(o)
            for row in csvreader:
                posts = row[4].split('|')
                geo = [ post for post in posts if not post.endswith('->,') ]
                csvwriter.writerow([row[0], len(posts), len(geo)])

# get_nposts_per_user('/Users/cchen224/Downloads/instagram_stats/merge_data_active.csv',
#                     '/Users/cchen224/Downloads/instagram_stats/posts_per_user_active.csv')
# get_nposts_per_user('/Users/cchen224/Downloads/instagram_stats/merge_data_regular.csv',
#                     '/Users/cchen224/Downloads/instagram_stats/posts_per_user_regular.csv')
# get_nposts_per_user('/Users/cchen224/Downloads/instagram_stats/merge_data.csv',
#                     '/Users/cchen224/Downloads/instagram_stats/posts_per_user.csv')

