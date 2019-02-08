import re, nltk
from bs4 import BeautifulSoup as bs
import urllib.parse
import urllib.request
import mysql.connector
import json
from dateutil.parser import parse
import time as delay

dberror = 0


# "01":32,"02":29,"03":32, "04":31, "05":32, "06":31, "07":32, "08":32,  "09":31,"10":32, "11":31
#
month = {
"12": 32
 }

article= "" # keep text


mydb = mysql.connector.connect(
  host="localhost",
  user="user",
  passwd="745812934",
  database="nytimes"
)

mycursor = mydb.cursor()

user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': user_agent}

for m, days in month.items():

    m = str(m)

    for n in range(1,days):
        url = "https://www.huffingtonpost.com/archive/2015-"+m+"-"+("%02d" % n)
        print (url)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                the_page = response.read()
            # print (response)
        except:
            print("error getting request")
            continue


        soup = bs(the_page, 'html.parser')
        cards = soup.select(".card__content")

        the_hrefs = []
        for c in cards:
            if c.select('.card__label span')[0].get_text() in ['BUSINESS','POLITICS','WORLDPOST']:
                the_hrefs.append(c.a.get('href'))
        for url in the_hrefs:
            try:
                print ("https://www.huffingtonpost.com" + url)
                req = urllib.request.Request("https://www.huffingtonpost.com" + url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    raw = response.read()

            except:
                print("error getting request")
                continue

            soup = bs(raw, 'html.parser')
            if soup.select(".headline__title"):
                title = soup.select(".headline__title")[0].get_text()
                title = title.replace("'", "\\'")
                title  = "'" + title + "'"
            else:
                title = "NULL"

            if soup.select(".author-card__name a"):
                author = soup.select(".author-card__name a")[0].get_text()
                author = "'" + author + "'"
            else:
                author = "NULL"

            if soup.select(".timestamp__date--published"):
                time = soup.select(".timestamp__date--published")[0].get_text()
                time = str(parse(time).date())
                time = "'" + time + "'"
            else:
                time = "NULL"

            url = "'" + url + "'"
            article = ""
            ps = soup.select(".entry__text p")
            for p in ps:
                words = p.get_text().strip()
                article = article + " " + words
            article = article.replace("'", "\\'")
            article = "'" + article + "'"
            sql = "insert into huffpost (title, url, author, date, text) \
            values (" + title + ", "+ url   +", " + author      + ", " + time + "," + article +  ")"
            print (time)
            try:
                mycursor.execute(sql)
                mydb.commit()
                # delay.sleep(1.5)
                pass
            except Exception as e:
                print (e)
                dberror=dberror+1
                print("**************db error ****************")
                print(e)
                continue
            print ("=======================================")
print ("Done.")
"""
        or c in cards:
    ...:     print (c.a.get('href'))

    c.select('.card__label span')
    cards = soup.select(".card__content")


# get the urls of the articles.
    for n in range(1,days):
        n = str(n)

        url="https://www.politico.com/magazine/story/"+n+"?advSearchDate="+m+"-2015"


        print (url)

        try:
            response = request.urlopen(url)
            print (response)
        except:
            print("error getting request")
            continue

        try:
            raw = response.read().decode('utf8')
        except Exception as e:
            print (e)
            continue

        soup = bs(raw, 'html.parser')


        urls = soup.select(".web-archive-results ul li .story-frag h3 a")
        # print (urls)

        # extract from each article.
        for u in urls:
            # print (u.get('href'))
            url = u.get('href')
            try:
                response = request.urlopen(url)
            except:
                print("********** error getting request ***********")
                continue
            try:
                raw = response.read().decode('utf8')
            except Exception as e:
                print (e)
                continue
            soup = bs(raw, 'html.parser')


            # (soup.select('.story-text p'))


            ###### put quotes on title and author #######

            if soup.select('span[itemprop="headline"]'):
                title = "'" + soup.select('span[itemprop="headline"]')[0].get_text() + "'"
                print (title)
            else:
                title = "NULL"

            if soup.time:
                thedate = soup.time.get('datetime')
                thedate = str(parse(thedate).date())
                thedate = "'" + thedate + "'"
                print(thedate)
            else:
                thedate = "NULL"

            if soup.select("footer p.byline"):
                author = "'" + soup.select("footer p.byline")[0].get_text().strip()+ "'"
            else:
                author = "NULL"

            ps = soup.select('.story-text > p')

            for p in ps:
                words = p.get_text()
                article = article + " " + words

            # print(article)
            article_str =  "'" + article + "'"
            article = ""


            # print (article_str)


            sql = "insert into politico (title, url, author, date, text) \
            values (" + title + ", '"+ url   +"', " + author      + ", " + thedate     + "," + article_str +  ")"
            print(sql)
            try:
                mycursor.execute(sql)
                mydb.commit()
                pass
            except Exception as e:
                print (e)
                dberror=dberror+1
                print("**************db error ****************")
                continue
            #print (article[:100])
            print (title + " " + thedate)
            print("--------------------------------------------")

print (str(dberror) + " database errors")

"""
