import folium
from geopy.geocoders import ArcGIS
from flask import Flask, render_template, request
import urllib.request, urllib.parse, urllib.error
import twurl
import ssl
import json


app = Flask(__name__)

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

# Ignores SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


@app.route('/', methods=['GET', 'POST'])
def send():
    """
    (None) -> web site
    Function consists of small functions, which have every own task to do.
    It's connected with an HTML file "design.html", which shows us two fields:
    first - to enter the account name and second - number of friends we want
    to see. When we press the button "submit", this function returns the map
    with all the locations of friends.
    """
    if request.method == 'POST':
        acct = request.form['acct']
        count = request.form['count']
        url = twurl.augment(TWITTER_URL,
                            {'screen_name': acct, 'count': count})
        connection = urllib.request.urlopen(url, context=ctx)
        data = connection.read().decode()

        def gettingInformation():
            """
            (None) -> dict
            Returns dictionary of the information about the friends specified
            in the "keys" list
            """
            finalDict = {}
            myList = []
            friends = json.loads(data)
            for element in friends["users"]:
                keys = ['id', 'screen_name', 'location', 'created_at',
                        'friends_count', 'lang', 'time_zone']
                dict1 = {}
                for key in keys:
                    dict1[key] = element[key]
                myList.append(dict1)
            finalDict["users"] = myList

            return finalDict

        def creatingMap():
            """
            (None) -> map
            Creates and returns the map
            """
            maps = folium.Map()

            return maps

        def listOfDcts():
            """
            (None) -> list
            Returns list of dictionaries with screen_name and location
            """
            listOfDicts = []
            myInfo = gettingInformation()
            for element in myInfo["users"]:
                keys = ['screen_name', 'location']
                dict1 = {}
                for key in keys:
                    dict1[key] = element[key]
                listOfDicts.append(dict1)
            return listOfDicts

        def finalDictionary():
            """
            (None) -> list
            Returns the list of dictionaries, where the key is location and
            the value is screen_name
            """
            listOfNameLoc = listOfDcts()
            result_dict = {}
            finalList = []
            for i in listOfNameLoc:
                newDict = {}
                newDict[i['location']] = [i['screen_name']]
                finalList.append(newDict)
            for di in finalList:
                for key, value in di.items():
                    result_dict.setdefault(key, []).extend(value)

            return result_dict

        def mainFunction():
            """
            (None) -> html
            Returns html type of the map, which could be further used to
            be redirected from the web site to our map
            """
            myMap = creatingMap()
            dictNameLoc = finalDictionary()
            geolocator = ArcGIS()

            friendsGroup = folium.FeatureGroup(name='Friends')
            for key, value in dictNameLoc.items():
                try:
                    location = geolocator.geocode(key)
                    locations = [location.latitude, location.longitude]
                    friendsGroup.add_child(folium.Marker(location=locations,
                         popup='<br>'.join(value),
                         icon=folium.Icon(color='black', icon='thumbs-up')))
                except:
                    pass

            myMap.add_child(friendsGroup)
            myMap.add_child(folium.LayerControl())
            htmlString = myMap.get_root().render()

            return htmlString

        return mainFunction()

    return render_template("design.html")


if __name__ == "__main__":
    app.run()
