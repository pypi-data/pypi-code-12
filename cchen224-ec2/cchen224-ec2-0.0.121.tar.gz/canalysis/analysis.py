#
# # with open('/Users/cchen224/Downloads/instagram_media.csv', 'r') as i:
# #     csvreader = csv.reader(i)
# #     with open('/Users/cchen224/Downloads/locations.csv', 'a') as o:
# #         csvwriter = csv.writer(o)
# #         [csvwriter.writerow([row[0], row[3], row[-4], row[-2], row[-1]]) for row in csvreader]
# # import random
# # with open('/Users/cchen224/Downloads/geo_sample.csv', 'a') as o:
# #     csvwriter = csv.writer(o)
# #     counter = 0
# #     for index in range(len(location_lat)):
# #         if location_lat[index] != '' and random.uniform(0, 1) < 0.001:
# #             counter += 1
# #             csvwriter.writerow([location_lat[index], location_long[index]])
# #         if counter >= 5000:
# #             break
#
#
#
# import csv
# from datetime import datetime, timedelta
#
# users = []
# create_at = []
# location_lat = []
# location_long = []
# location_id = []
#
# with open('/Users/cchen224/Downloads/locations.csv', 'r') as i:
#     csvreader = csv.reader(i)
#     for row in csvreader:
#         users.append(row[0])
#         create_at.append(row[1])
#         location_id.append(row[2])
#         location_lat.append(row[3])
#         location_long.append(row[4])
# dt = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in create_at]
#
# # y = 0
# # y_l = 0
# # m = 0
# # m_l = 0
# # w_l = 0
# # w = 0
# # now = datetime.now()
# # for i in range(len(create_at)):
# #     if now - create_at[i] <= timedelta(days=365):
# #         y += 1
# #         if location_lat[i] != '':
# #             y_l += 1
# #         if now - create_at[i] <= timedelta(days=30):
# #             m += 1
# #             if location_lat[i] != '':
# #                 m_l += 1
# #             if now - create_at[i] <= timedelta(days=7):
# #                 w += 1
# #                 if location_lat[i] != '':
# #                     w_l += 1
#
# from geopy.geocoders import Nominatim
# import csv
#
# def get_city_country(lat, long):
#     pair = str(lat) + ', ' + str(long)
#     location = Nominatim().reverse(pair).raw['address']
#     try:
#         city = location['city'].encode('utf-8')
#     except:
#         city = ''
#     try:
#         country = location['country'].encode('utf-8')
#     except:
#         country = ''
#     return city, country
#
# locations = dict()
# with open('/Users/cchen224/Downloads/location_.csv', 'w') as o:
#     csvwriter = csv.writer(o)
#     for i in range(len(users)):
#         if location_lat[i] != '':
#             if location_id[i] not in locations:
#                 city, country = get_city_country(location_lat[i], location_long[i])
#                 locations[location_id[i]] = city, country
#             else:
#                 city, country = locations[location_id[i]]
#         else:
#             city = ''
#             country = ''
#         csvwriter.writerow([users[i], create_at[i], city, country])
#         # user = users[i]
#         # if user not in u:
#         #     u[user] = ''
#         # elif u[user] != '':
#         #     continue
#         # elif location_lat[i] != '':
#         #     city, country = get_city_country(location_lat[i], location_long[i])
#         #     u[user] = country
#
#
#
#
# import matplotlib.pyplot as plt
#
# total = dict()
# for user in users:
#     if user not in total:
#         total[user] = 1
#     else:
#         total[user] += 1
# plt.hist([val for val in total.values()], bins=50)
# plt.hist([val for val in total.values() if val < 50], bins=25)
#
# geo = dict()
# for index in range(len(users)):
#     if users[index] not in geo:
#         geo[users[index]] = 1
#     elif location_lat[index] != '':
#         geo[users[index]] += 1
# plt.hist([float(geo[key]) / total[key] for key in total.keys()], bins=50)
# plt.hist([float(geo[key]) / total[key] for key in total.keys() if total[key] != 1], bins=50)
#
# checkins = dict()
# for index in range(len(users)):
#     if location_lat[index] != '':
#         if users[index] not in checkins:
#             checkins[users[index]] = [(float(location_lat[index]), float(location_long[index]))]
#         else:
#             checkins[users[index]].append((float(location_lat[index]), float(location_long[index])))
#
# def get_rg(list):
#     from geopy.distance import great_circle
#     import math
#     t_lat = 0.
#     t_lon = 0.
#     for item in list:
#         lat, long = item
#         t_lat += lat
#         t_lon += long
#     m_lat = t_lat / len(list)
#     m_lon = t_lon / len(list)
#     d = []
#     for item in list:
#         d.append(great_circle(item, (m_lat, m_lon)).miles)
#         # d.append((item[0], m_lat) ** 2)
#         # d.append((item[1] - m_lon) ** 2)
#     return math.sqrt( sum(d) / len(list) )
# checkins_dist = [get_rg(checkins[key]) for key in checkins.keys()]
# plt.hist(checkins_dist, bins=50, range=[0,80])
# plt.ylabel('frequency')
# plt.xlabel('rg (miles)')
# plt.show()
#
# u_friends = dict()
# u_media = dict()
# u_followers = dict()
# with open('/Users/cchen224/Downloads/instagram_media_users.csv', 'r') as i:
#     csvreader = csv.reader(i)
#     for row in csvreader:
#         u_followers[row[0]] = row[2]
#         u_friends[row[0]] = row[3]
#         u_media[row[0]] = row[4]
# plt.hist([int(val) for val in u_followers.values()], bins=50)
# plt.hist([int(val) for val in u_followers.values() if int(val) < 5000], bins=50)
# plt.hist([int(val) for val in u_friends.values() if int(val) < 5000], bins=50)
# # plt.hist([float(u_followers[key]) / float(u_friends[key]) for key in u_media.keys() if float(u_friends[key]) != 0. and float(u_followers[key]) / float(u_friends[key]) < 5000], bins=50)
#
# post_perweek = dict()
# for i in range(len(users)):
#     key = users[i] + '@' + dt[i].strftime('%w')
#     if location_lat[i] != '':
#         if key not in post_perweek:
#             post_perweek[key] = 1
#         else:
#             post_perweek[key] += 1
#
#
# week_t = []
# week = []
# for i in range(len(users)):
#     week_t.append( dt[i].strftime('%d') )
#     if location_lat[i] != '':
#         week.append( dt[i].strftime('%d') )
# week = [int(day) for day in week]
# week_t = [int(day) for day in week_t]
# week_p = []
# for i in range(1,32):
#     week_p.append( float(len([item for item in week if item == i])) / len([item for item in week_t if item == i]))
# plt.plot(range(1,32), week_p)
# plt.xlabel('Day over month')
# plt.ylabel('Geocoded Percentage')
# plt.show()
#
# plt.hist(week_t, label='overall', bins=31, range=[1,32])
# plt.hist(week, label='geo-coded', bins=31, range=[1,32])
# plt.legend(loc='upper right')
# plt.show()
#
# users = dict()
# for item in uout: users[item] = 1
# for i in range(len(users)):
#     if users[i] in users:
#
#
#
#
#
# import pandas as pd
# data = pd.read_csv('/Users/cchen224/Downloads/locations.csv', header=None)
#
#
# import csv
# with open('/Users/cchen224/Downloads/instagram_media_users.csv', 'r') as i:
#     csvreader = csv.reader(i)
#     with open('/Users/cchen224/Downloads/instagram_media.csv', 'w') as o:
#         csvwriter = csv.writer(o)
#         for row in csvreader:
#             if int(row[4]) > 20:
#                 csvwriter.writerow(row)

def most_common(lst):
    return max(set(lst), key=lst.count)


import csv
location_dict = dict()
location_country = dict()
with open('/Users/cchen224/Downloads/instagram_stats/locations.csv', 'r') as location_input:
    csvreader = csv.reader(location_input)
    for row in csvreader:
        location_dict[row[0]] = row[7]
        location_country[row[7]] = [0, 0]

location_country['undefined'] = [0, 0]
with open('/Users/cchen224/Downloads/instagram_stats/merge_data_regular.csv', 'r') as i:
    csvreader = csv.reader(i)
    for row in csvreader:
        posts = row[4].split('|')
        user_geo_countries = [location_dict.get(post.split('@')[1].split('->')[1], '') for post in posts if not post.endswith('@->,')]
        has_country = False
        if user_geo_countries:
            has_country = True
            user_country = most_common(user_geo_countries)
            if user_country != '':
                location_country[user_country][0] += len(posts)
                location_country[user_country][1] += len(user_country)
        if not has_country:
            location_country['undefined'][0] += len(posts)
            location_country['undefined'][1] += 1


with open('/Users/cchen224/Downloads/instagram_stats/overall/country_regular.csv', 'a') as o:
    csvwriter = csv.writer(o)
    for country in location_country:
        out = [country]
        out.extend(location_country[country])
        csvwriter.writerow(out)