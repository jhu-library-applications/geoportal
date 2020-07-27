import requests
from bs4 import BeautifulSoup as Soup
from rdflib import Namespace, Graph, URIRef


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


def verifyHeadingList(searchList):
    all_items = []
    for item in searchList:
        print(item)
        vocab = item.get('vocab')
        searchTerm = item.get('term')
        print(vocab)
        print(searchTerm)
        if searchTerm:
            searchTerm.rstrip('.')
            type = authorities.get(vocab)
            if vocab != 'fast':
                url = baseURL+type+'/label/'+searchTerm
                try:
                    data = lc.get(url, timeout=30, headers=headers)
                    foundName = data.ok
                    newURL = data.url
                    if foundName:
                        newURL = data.url
                        newURL = newURL.replace('.html', '')
                        print(newURL)
                        graph = getGraph(newURL+'.nt', 'nt')
                        if graph:
                            for result in graph.subject_objects((mads.authoritativeLabel)):
                                if auth+type in result[0]:
                                    if result[1].value == searchTerm:
                                        print('Heading validated')
                                        item['authURI'] = result[0]
                                        item['authLabel'] = result[1].value
                except requests.Timeout:
                    pass
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
                    print(authLabel)
                    if authLabel == searchTerm:
                        print('Heading validated')
                        item['authLabel'] = authLabel
                        item['authURI'] = identifier
        all_items.append(item)
    return all_items
