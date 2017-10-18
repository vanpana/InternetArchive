from urllib.request import urlopen
import feedparser
import urllib
import re
import shutil

from pip._vendor import requests


def getHTMLFile(url, filename):
    '''
    # Write the contents to a text file (overwriting the file if it already exists!)
    :param url: string
    :param filename: string (must also contain extension)
    :return: nothing
    '''
    # Open the web document for reading
    web_page = urlopen(url)

    # Read its contents as a Unicode string
    web_page_contents = web_page.read().decode('UTF-8')

    html_file = open(filename, 'w', encoding='UTF-8')
    html_file.write(web_page_contents)
    html_file.close()

def getWorldURL(url):
    '''
    # Get the feed link of the World news section.
    :param url: string
    :return: url string
    '''
    # Open the web document for reading
    web_page = urlopen(url)

    # Read its contents as a Unicode string
    web_page_contents = web_page.read().decode('UTF-8')

    searchObj = re.search(r'.*Top Stories.*<a\s+(?:[^>]*?\s+)?href=(["\'])(.*?)\1.*World.*', web_page_contents, re.M | re.I)

    #TODO: Check if not null
    return "http://www.abc.net.au" + searchObj.group(2)


def downloadWorldXML(url, filename):
    '''
    Downloads XML feed from the url provided
    :param url: string
    :param filename: string, path/to/file
    :return: nothing, just writes file on the disk
    '''
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)


def cleanhtml(raw_html):
    '''
    Cleans html tags
    :param raw_html: html string
    :return: clean html string, with no tags
    '''
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def getXMLData(filename, tag, noOfItems = 10):
    '''
    Parse XML feed data.
    :param filename: XML path/to/file
    :param tag: title, link, description, image
    :param noOfItems: how many entries to be generated, default is 10
    :return: list of strings of data
    '''
    head = 2
    filename = "file://" + filename
    web_page_contents = urlopen(filename).read().decode('UTF-8')
    titles = []

    tag = tag.lower()

    if tag == "description":
        tag = "p"
        head = 0

    if tag == "image":
        searchobj = re.findall(r'<media:content url=\".*940x627\.jpg', web_page_contents, re.M | re.I)
        head = 0
        for obj in searchobj:
            titles.append(obj.strip("<media:content url=\""))

    else:
        searchobj = re.findall(r'<' + tag + '>.*<\/' + tag + '>', web_page_contents, re.M | re.I)

        for obj in searchobj:
            titles.append(cleanhtml(obj))

    return titles[head:2 + noOfItems]

def generateMyHTML(titles, links, description, images):
    pass

#print(getWorldURL())
# downloadWorldXML(getWorldURL(), "/Users/vanpana/Desktop/InternetArchive/world.xml")

# print(getTitlesXML("/Users/vanpana/Desktop/InternetArchive/world.xml", 2))

print(getXMLData("/Users/vanpana/Desktop/InternetArchive/world.xml", "title", 4))
print(getXMLData("/Users/vanpana/Desktop/InternetArchive/world.xml", "link", 4))
print(getXMLData("/Users/vanpana/Desktop/InternetArchive/world.xml", "description", 4))
print(getXMLData("/Users/vanpana/Desktop/InternetArchive/world.xml", "image", 4))



#writeToFile("http://www.abc.net.au/news/feeds/rss/", "/Users/vanpana/Desktop/InternetArchive/abc.html")

### Some regex for abc net feed
# Getting the world feed link


####
# Some regex for techcrunch
# Getting the titles
# cat test.html | grep " data-permalink=\".*\"" | sed 's/.*"\(.*\)"[^"]*$/\1/'

# Getting the pics
# cat test.html | grep " data-omni-sm=\".*\"" | grep " data-src=" | sed 's/.*data-src=\"\(.*\)\".*/\1/g'

# Getting desc (maybe)
# cat test.html | grep "excerpt" | sed "s/.*excerpt\">\(.*\).*$/\1/g" | sed "s/.*content=\"\(.*\)\".*/\1/g" | grep -v "<"


