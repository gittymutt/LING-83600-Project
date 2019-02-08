import re, nltk
from bs4 import BeautifulSoup as bs
from urllib import request
import mysql.connector
import json
from dateutil.parser import parse

dberror = 0
month = {
"01":32,"02":29,"03":32, "04":31, "05":32, "06":31, "07":32, "08":32,
 "09":31, "10":32, "11":31, "12": 32 }
# month = {"01":2}
article= "" # keep text

for m, days in month.items():

# get the urls of the articles.
    for n in range(1,days):

        url = "https://www.breitbart.com/politics/2015/" + m + "/" + ("%02d" % n) + "/"
        print (url)

        try:
            response = request.urlopen(url)
        except:
            print("error getting request")
            continue

        try:
            raw = response.read().decode('utf8')
        except Exception as e:
            print (e)
            continue

        soup = bs(raw, 'html.parser')


        urls = soup.select("article h2 a")


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

            ###### put quotes on title and author #######

            if soup.h1:
                title = "'" + soup.h1.get_text() + "'"
            else:
                title = "NULL"

            if soup.select("footer.byline address"):
                author = "'" + soup.select("footer.byline address")[0].get("data-aname").title() + "'"
            else:
                author = "NULL"

            if soup.time:
                thedate = soup.time.get('datetime')
                thedate = str(parse(thedate).date())
                thedate = "'" + thedate + "'"
                print(thedate)
            else:
                thedate = "NULL"


            ps = soup.select("div.entry-content p")

            for p in ps:
                words = p.get_text()
                article = article + " " + words

            article_str =  "'" + article + "'"
            article = ""

            mydb = mysql.connector.connect(
              host="localhost",
              user="mutt",
              passwd="#$%^&*",
              database="nytimes"
            )

            mycursor = mydb.cursor()
            sql = "insert into breitbart_raw (title, url, author, date, text) \
            values (" + title + ", '"+ url   +"', " + author      + ", " + thedate     + "," + article_str +  ")"
            # print(sql)
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
