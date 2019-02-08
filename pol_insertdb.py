import re, nltk
from bs4 import BeautifulSoup as bs
from urllib import request
import mysql.connector
import json
from dateutil.parser import parse

dberror = 0



month = {
"JANUARY":10,"FEBRUARY":9,"MARCH":13, "APRIL":12, "MAY":11, "JUNE":14, "JULY":12, "AUGUST":11,
 "SEPTEMBER":11, "OCTOBER":10, "NOVEMBER":9, "DECEMBER": 9 }

article= "" # keep text
mydb = mysql.connector.connect(
  host="localhost",
  user="mutt",
  passwd="&*()^^^",
  database="nytimes"
)

mycursor = mydb.cursor()

for m, days in month.items():
    # print (https://www.politico.com/magazine/story/1?advSearchDate=DECEMBER-2015)
    m = str(m)

# get the urls of the articles.
    for n in range(1,days+1):
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
