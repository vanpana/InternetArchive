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

def getTodayString():
    '''
    Gets today's date as a string.
    :return: string (DD.MM.YYYY)
    '''
    now = datetime.datetime.now()
    return calendar.day_abbr[now.weekday()] + "," + str(now.day) + "." + str(now.month) + "." + str(now.year)

def getArchiveList():
    '''
    Gets the list of all existent archived pages.
    :return: list of dates
    '''
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
    '''
    Get 5 lists of things needed to construct a web page
    :param url: url of the website to parse
    :param no_of_items: how many entries to be generated, default is 10
    :return: list of ttles, links, descriptions, images, pubdate
    '''
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
    '''
    Writes parsed data to file
    :param url: url of the website to parse
    :param filename: XML path/to/file to be written
    :param no_of_items: how many entries to be generated, default is 10
    :return: nothing, just writes a file on the disk
    '''
    print("Started writing to file!")
    titles, links, descriptions, images, pubdate = getParsedData(url, no_of_items)

    with open(filename, "w") as file:
        for index in range(0, len(titles)):
            file.write(titles[index] + "\n" + links[index] + "\n" + descriptions[index] + "\n" + \
                       images[index] + "\n" + pubdate[index]+ "\n")

def readParsedDataFromFile(filename):
    '''
    Gets the data from file and returns it
    :param filename: XML path/to/file to read
    :return: list of ttles, links, descriptions, images, pubdate
    '''
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
    '''
    Generate own signature.
    :param archive_date: date when html was archived
    :param source_url: url where it was archived from
    :return: signature string
    '''
    string = "<center><h1><font color=\"#415274\">ABC World News Archive</font></h1>\n"
    string += "<h2><font color=\"#415274\">" + archive_date + "</font></h2>\n"
    string += "<img src=\"../abclogo.gif\">\n"
    string += "<p><b>Source: </b>" + "<a href=" + source_url + ">" + source_url + "</a></p>\n"
    string += "<p><b>Archivist:</b> YOUR NAME GOES HERE</p></center>\n<hr>\n"

    return string


def generateStory(numberInQueue, title, link, description, image, date):
    '''
    Generate stories for html
    :param numberInQueue: number from total number of stories
    :param title: string
    :param link: string
    :param description: string
    :param image: string
    :param date: string
    :return: story string
    '''
    string = "\n"
    string += "<center><h1>" + str(numberInQueue) + ". " + title + "</h1>\n"
    string += "<img src=" + image + ">\n"
    string += "<h4>" + description + "</h4>\n"
    string += "<p><b>Link to full story:</b> " + "<a href=" + link + ">" + link + "</a></p>\n"
    string += "<p><b>Publication date:</b> " + date + "</p></center>\n<hr>\n"

    return string


def generateMyHTML(archive_date, source_filename, dest_filename, source_url=getWorldURL("http://www.abc.net.au/news/feeds/rss/")):
    '''
    HTML generator
    :param archive_date: date when it was archived
    :param source_filename: raw text file
    :param dest_filename: where html will be saved
    :param source_url: data source, defaul is abc.net.au rss feed
    :return:
    '''
    titles, links, descriptions, images, pubdate = readParsedDataFromFile(source_filename)

    string = "<!DOCTYPE html>\n<html>\n<head>\n<body bgcolor=\"#E6E6FA\">\n"
    string += generateSignature(archive_date, source_url)

    for index in range(0, len(titles)):
        string += generateStory(index + 1, titles[index], links[index], descriptions[index], images[index], pubdate[index])

    string += "</body>\n</head>\n</html>\n"

    with open(dest_filename, "w") as file:
        file.write(string)

#-------------- Tkinter --------------#

# Func #
def getSelection():
    '''
    Get listbox selected text
    :return: selected date
    '''
    selection = lbox.get(lbox.curselection(), (lbox.curselection()))[0]
    if selection == "latest":
        selection = getTodayString()
    return selection

def extractNews():
    '''
    Generate html from raw text. Shows error text in case no raw text exists or no item is selected.
    '''
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
    '''
    Displays html in browser. Shows error text in case no html is generated or no item is selected.
    '''
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
    '''
    Generates raw text for today's latest news
    '''
    writeParsedDataToFile("http://www.abc.net.au/news/feeds/rss/", "archive/" + getTodayString() + ".txt")
    infotext.config(text="Fetched latest news!")

# UI #
print(getArchiveList())
root = Tk()
root.title("ABC News Archive")

logoimg = PhotoImage(file="abclogo.gif")
logo = Label(root, image=logoimg).pack(side="top")

lbox = Listbox(root)

extract = Button(root, text="Extract news from archive", command=extractNews)
display = Button(root, text="Display news from archive", command=displayNews)
latest = Button(root, text="Fetch latest news", command=fetchLatestNews)
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