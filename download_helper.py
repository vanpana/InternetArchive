import webbrowser
from pathlib import Path
from tkinter import *
from urllib.request import urlopen


import datetime
import calendar
import re
import os

from os.path import isfile, join
from pip._vendor import requests

def getTodayFolderName():
    now = datetime.datetime.now()
    return str(now.day) + "." + str(now.month) + "." + str(now.year)

def getTodayString():
    now = datetime.datetime.now()
    return calendar.day_abbr[now.weekday()] + "," + str(now.day) + "." + str(now.month) + "." + str(now.year)

def getArchiveList():
    mypath = "archive/"
    templist = [f for f in os.listdir(mypath) if isfile(join(mypath, f))]

    myarchive = []
    for link in templist:
        if ".txt" in link:
            myarchive.append(link.strip(".txt"))

    return myarchive

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
    print("Generated World URL")
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


def getXMLData(filename, tag, no_of_items = 10):
    '''
    Parse XML feed data.
    :param filename: XML path/to/file
    :param tag: title, link, description, image, date
    :param no_of_items: how many entries to be generated, default is 10
    :return: list of strings of data
    '''
    head = 2
    filename = "file://" + os.path.dirname(os.path.realpath(__file__)) + "/" + filename
    web_page_contents = urlopen(filename).read().decode('UTF-8')
    titles = []

    tag = tag.lower()

    if tag == "date":
        tag = "pubdate"

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

    return titles[head:2 + no_of_items]

def getParsedData(url, no_of_items = 10):
    url = getWorldURL(url)
    temp_file_name = "temp.xml"
    downloadWorldXML(url, temp_file_name)

    titles = getXMLData(temp_file_name, "title", no_of_items)
    links = getXMLData(temp_file_name, "link", no_of_items)
    descriptions = getXMLData(temp_file_name, "description", no_of_items)
    images = getXMLData(temp_file_name, "image", no_of_items)
    pubdate = getXMLData(temp_file_name, "pubdate", no_of_items)

    os.remove("temp.xml")

    return titles, links, descriptions, images, pubdate

def writeParsedDataToFile(url, filename, no_of_items=10):
    print("Started writing to file!")
    titles, links, descriptions, images, pubdate = getParsedData(url, no_of_items)

    with open(filename, "w") as file:
        for index in range(0, len(titles)):
            file.write(titles[index] + "\n" + links[index] + "\n" + descriptions[index] + "\n" + \
                       images[index] + "\n" + pubdate[index]+ "\n")

def readParsedDataFromFile(filename):
    titles, links, descriptions, images, pubdate = [], [], [], [], []
    with open(filename, "r") as file:
        for line in file:
            titles.append(line.strip("\n"))
            links.append(file.readline().strip("\n"))
            descriptions.append(file.readline().strip("\n"))
            images.append(file.readline().strip("\n"))
            pubdate.append(file.readline().strip("\n"))

    return titles, links, descriptions, images, pubdate



#-------------- HTML Generation --------------#

def generateSignature(archive_date, source_url):
    string = "<center><h1><font color=\"#415274\">ABC World News Archive</font></h1>\n"
    string += "<h2><font color=\"#415274\">" + archive_date + "</font></h2>\n"
    string += "<img src=\"../abclogo.gif\">\n"
    string += "<p><b>Source: </b>" + "<a href=" + source_url + ">" + source_url + "</a></p>\n"
    string += "<p><b>Archivist:</b> YOUR NAME GOES HERE</p></center>\n<hr>\n"

    return string


def generateStory(numberInQueue, title, link, description, image, date):
    string = "\n"
    string += "<center><h1>" + str(numberInQueue) + ". " + title + "</h1>\n"
    string += "<img src=" + image + ">\n"
    string += "<h4>" + description + "</h4>\n"
    string += "<p><b>Link to full story:</b> " + "<a href=" + link + ">" + link + "</a></p>\n"
    string += "<p><b>Publication date:</b> " + date + "</p></center>\n<hr>\n"

    return string


def generateMyHTML(archive_date, source_filename, dest_filename, source_url=getWorldURL("http://www.abc.net.au/news/feeds/rss/")):
    titles, links, descriptions, images, pubdate = readParsedDataFromFile(source_filename)

    string = "<!DOCTYPE html>\n<html>\n<head>\n<body bgcolor=\"#E6E6FA\">\n"
    string += generateSignature(archive_date, source_url)

    for index in range(0, len(titles)):
        string += generateStory(index + 1, titles[index], links[index], descriptions[index], images[index], pubdate[index])

    string += "</body>\n</head>\n</html>\n"

    with open(dest_filename, "w") as file:
        file.write(string)



# writeParsedDataToFile("http://www.abc.net.au/news/feeds/rss/", "archive/Wed, 18.10.2017.txt")
# print(readParsedDataFromFile("archive/Wed, 18.10.2017.txt"))
# generateMyHTML(getTodayString(), "archive/Wed, 18.10.2017.txt", "archive/firstgenerated.html")

#-------------- Tkinter --------------#

# Func #
def getSelection():
    selection = lbox.get(lbox.curselection(), (lbox.curselection()))[0]
    if selection == "latest":
        selection = getTodayString()
    return selection

def extractNews():
    if lbox.curselection() == ():
        infotext.config(text="No item selected!")
    else:
        selection = getSelection()

        if not Path("archive/" + selection + ".txt").is_file():
            infotext.config(text="Latest news not fetched!")
        else:
            generateMyHTML(selection, "archive/" + selection + ".txt", "archive/" + selection + ".html")
            infotext.config(text="Archive for " + selection + " extracted!")

def displayNews():
    if lbox.curselection() == ():
        infotext.config(text="No item selected!")
    else:
        selection = getSelection()
        filename = os.path.dirname(os.path.realpath(__file__)) + "/archive/" + selection + ".html"

        if not Path(filename).is_file():
            infotext.config(text="Archive for " + selection + " not extracted yet!")
        else:
            filename = "file://" + os.path.dirname(os.path.realpath(__file__)) + "/archive/" + selection + ".html"
            webbrowser.open(filename)

def fetchLatestNews():
    writeParsedDataToFile("http://www.abc.net.au/news/feeds/rss/", "archive/" + getTodayString() + ".txt")
    infotext.config(text="Fetched latest news!")

# UI #
print(getArchiveList())
root = Tk()
root.title("ABC News Archive")

logoimg = PhotoImage(file="abclogo.gif")
# w1 = Label(root, image=logo).pack(side="top")
# w2 = Label(root,
#            justify=LEFT,
#            padx = 10,
#            text="da\ndadadada\nfdsafas").pack(side="bottom left")
# w3 = Label(root,
#            justify=LEFT,
#            padx = 10,
#            text="fdsaga\ndfvnfgnfa\nfytryrtfas").pack(side="bottom right")



logo = Label(root, image=logoimg).pack(side="top")

lbox = Listbox(root)

extract = Button(root, text="Extract news from archive", command=extractNews)
display = Button(root, text="Display news from archive", command=displayNews)
latest = Button(root, text="Fetch latest news", command=fetchLatestNews())
infotext = Label(text="Welcome to the archive!")

lbox.pack()
extract.pack()
display.pack()
latest.pack()
infotext.pack()

for item in getArchiveList():
    if item != getTodayString():
        lbox.insert(END, item)
lbox.insert(END,"latest")

root.mainloop()





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


