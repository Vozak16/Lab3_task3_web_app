import urllib.request
import urllib.parse
import urllib.error
import twurl
import json
import ssl
import certifi
import geopy.geocoders
import folium


def twitter_dict_get(twitter_url, username):
    """
    Returns the dictionary from twitter url.
    :param twitter_url: string
           username: string
    :return: dictionary
    """
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    acct = username

    url = twurl.augment(twitter_url,
                        {'screen_name': acct, 'count': '100'})

    connection = urllib.request.urlopen(url, context=ctx)
    data = connection.read().decode()
    type(data)
    js = json.loads(data)

    return js


def locations_friend_names_dct(dict_from_file):
    """
    Returns dictionary, where keys are locations and values are friend names.
    :param dict_from_file: dict
    :return: dict
    """
    location_names_dct = {}
    for i in dict_from_file["users"]:
        if i["location"] in location_names_dct.keys():

            location_names_dct[i["location"]] += ', ' + i["name"]
        elif i["location"].strip() != '':

            location_names_dct[i["location"]] = i["name"]

    return location_names_dct


def address_to_cordinates(location_string):
    """

    Takes the address and returns two float numbers - latitude and longtitude.
    :param location_string: string
    :return:float
    """
    geopy.geocoders.options.default_ssl_context = ssl.create_default_context(
        cafile=certifi.where())

    geolocator = geopy.geocoders.Nominatim(timeout=15,
                                           user_agent="specify_your_app_name")
    """from geopy.extra.rate_limiter import RateLimiter
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)"""

    try:
        location = geolocator.geocode(location_string)

        return location.latitude, location.longitude
    except AttributeError:

        return None


def location_dct_to_coord_lst(dict_location_names):
    """
    Returns list with tuples where the first element is
    the pair of coordinates and the second one is user names.
    :param dict_location_names: dict
    :return: list
    """
    dict_coord_names = {}
    for i in dict_location_names:
        if address_to_cordinates(i) is not None:
            pair_coord = address_to_cordinates(i)
            if pair_coord in dict_coord_names.keys():
                dict_coord_names[pair_coord] += ', ' + dict_location_names[i]
            else:
                dict_coord_names[pair_coord] = dict_location_names[i]

    lst_coord_names = []
    for i in dict_coord_names:
        lst_coord_names.append((dict_coord_names[i], i))

    return lst_coord_names


def map_create(lst_titles_and_coordinates):
    """
    Creates a map using coordinates and matches marker with titles.
    Also creates additional layer
    with lighted countries, where the most films in the world were filmed.
    :param : lst_titles_and_coordinates: list
           : year: string
    :return: None
    """
    mapp = folium.Map()
    fg_first = folium.FeatureGroup(name="The user's friends locations!")
    for i in lst_titles_and_coordinates:
        fg_first.add_child(folium.Marker(location=[i[1][0],
                                         i[1][1]], popup=i[0]))

    mapp.add_child(fg_first)
    mapp.add_child(folium.LayerControl())

    mapp.save('friend_locations_map.html')
    my_map = mapp.get_root().render()
    return my_map


def main(username):
    # https://apps.twitter.com/
    # Create App and get the four strings, put them in hidden.py

    twitter_url = 'https://api.twitter.com/1.1/friends/list.json'

    user_name_dict = twitter_dict_get(twitter_url, username)
    print("Please, wait from 10 seconds to one minute map is generating.")
    return map_create(location_dct_to_coord_lst(locations_friend_names_dct
                                                (user_name_dict)))

