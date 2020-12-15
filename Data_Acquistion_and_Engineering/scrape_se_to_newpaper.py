import requests
from pyden.connect.gsearch_api.google import google
from pyden.newspaper.newspaper import Article
from pyden.google_api.search import gsearch
import time
import unidecode

#npm install se-scraper
# run with sudo docker run -p 3000:3000 tschachn/se-scraper:latest

class Object(object):
    pass


toscrape = ["https://amwalalghad.com", "https://www.mubasher.info/markets/ADX/stocks/NBAD/news", "https://amwalalghad.com", "https://www.alarabiya.net/ar/tools"]

def gsearch(term, pages = 2):
    term = term.replace("\"","").replace("\'","").replace("-", "")
    term += " -filetype:pdf"  #TODO: be able to read pdfs
    data = '{ "browser_config": { "random_user_agent": true },"scrape_config": { "search_engine": "google","keywords": ["'+term+'"],"num_pages": '+str(pages)+'}}'
    header = {'Content-Type': 'application/json'}
    results = requests.post("http://0.0.0.0:3000", data = data, headers = header).json()
    output = []

    for num in range(int(pages)):
        if str(num+1) in results['results'][term]:
            output.extend([i for i in results['results'][term][str(num+1)]['results']])
    return output

def search(query, link = ""):
    unaccented_string = unidecode.unidecode(query)
    query_outs = gsearch(unaccented_string)
    titles = []
    labels = []
    para = []
    rm = []
    outputs = [Object() for _ in query_outs]

    for i, qo in enumerate(query_outs):
        query = outputs[i]; query.link = qo['link']
        # if not query.link or query.link.replace('/', u'\u2215') == link[0]:  # the links have '/' replaced
        #     rm.append(i)
        #     continue
        art = Article(query.link)  # if you are an article, parse and
        try:
            start = time.time()
            art.download()
            if not art.html:
                rm.append(i)
                continue
            print(query.link)
            print("took " + str(time.time() - start))
            art.parse()  # some articles cannot be parsed
            para.append(art.text.split("\n\n"))  # this makes paras a list of lists
            toadd = query.link.replace('/', u'\u2215')
            if len(query.link) > 255:
                toadd = toadd[:255]
            labels.append(toadd)  # titles are the labels that things are saved by
            query.title = art.title
            if art.title == "":
                query.title = qo[i]['title']  # this is just going to be what the title was on google
            query.sources = art.source_url
            query.authors = art.authors
            if art.publish_date:
                query.date = art.publish_date.strftime('%m/%d/%Y')
        except Exception as e:
            print(e)  # if u cant load it uhhhh just dont do anything
    for index in sorted(rm, reverse=True):
        del outputs[index]
    return outputs, labels, para, titles


results = search("site:" + toscrape[0] + " fab")
print(results)
