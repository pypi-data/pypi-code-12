# from geopy.geocoders import Nominatim
#
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