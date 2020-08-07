import requests
from bs4 import BeautifulSoup as Soup
from rdflib import Namespace, Graph, URIRef
from fuzzywuzzy import fuzz


# Configuration for requests.
headers = {'User-Agent': 'Custom user agent'}
lc = requests.Session()
ft = requests.Session()
baseURL = 'http://id.loc.gov/authorities/'
fastURL = 'http://id.worldcat.org/fast/search?query=cql.any+all+%22'
fastPara = '%22&fl=oclc.heading&recordSchema=info:srw/schema/1/rdf-v2.0'
mads = Namespace('http://www.loc.gov/mads/rdf/v1#')
auth = URIRef('http://id.loc.gov/authorities/')
authorities = {'lcnaf': 'names',
               'lcsh': 'subjects',
               'genre': 'genreForms'}


def getGraph(url, format):
    g = Graph()
    try:
        data = lc.get(url, timeout=30, headers=headers)
        data = data.text
        graph = g.parse(data=data, format=format)
    except requests.exceptions.Timeout:
        graph = None
    return graph


def findTermFromLabel(searchTerm, type):
    newURL = None
    url = baseURL+type+'/label/'+searchTerm
    try:
        data = lc.get(url, timeout=30, headers=headers)
        foundName = data.ok
        newURL = data.url
        if foundName:
            newURL = data.url
            if newURL:
                newURL = newURL.replace('.html', '')
                return newURL
    except requests.Timeout:
        pass


def getInfoFromGraph(graph, item, searchTerm, type):
    if graph:
        for result in graph.subject_objects((mads.authoritativeLabel)):
            if auth+type in result[0]:
                ratio = fuzz.ratio(result[1].value, searchTerm)
                if ratio > 95:
                    print('Heading validated')
                    item['authURI'] = result[0].toPython()
                    item['authLabel'] = result[1].value


def verifyHeadingList(searchList):
    all_items = []
    for item in searchList:
        searchTerm = item.get('term')
        if searchTerm:
            vocab = item.get('vocab')
            type = authorities.get(vocab)
            print(vocab)
            print(searchTerm)
            if vocab != 'fast':
                if item.get('uri') != 'None':
                    newURL = item.get('uri')
                    graph = getGraph(newURL+'.nt', 'nt')
                    getInfoFromGraph(graph, item, searchTerm, type)
                else:
                    newURL = findTermFromLabel(searchTerm, type)
                    if newURL:
                        graph = getGraph(newURL+'.nt', 'nt')
                        getInfoFromGraph(graph, item, searchTerm, type)
            else:
                data = ft.get(fastURL+searchTerm+fastPara)
                data = data.content
                soup = Soup(data, features='lxml')
                record = soup.find('record')
                if record:
                    identifier = record.find('dct:identifier')
                    identifier = identifier.string
                    authLabel = record.find('skos:preflabel')
                    authLabel = authLabel.string
                    if authLabel == searchTerm:
                        print('Heading validated')
                        item['authLabel'] = authLabel
                        item['authURI'] = identifier
        del item['uri']
        print(item)
        all_items.append(item)
    return all_items
