import urllib
import urllib2
import json

# Get Data
url = "https://api.foursquare.com/v2/venues/search?near=chicago,IL"
values = {'location' : 'chicago,IL'}

data = urllib.parse.urlencode(values)
b_data = data.encode('utf8') #binary data
request = urllib.request.Request(url,b_data)
response = urllib.request.urlopen(request)
data = response.read()
# Work on Data
parsed_data = json.loads(data)

