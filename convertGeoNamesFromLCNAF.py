import requests
from rdflib import Namespace, Graph, URIRef, RDFS
from bs4 import BeautifulSoup as Soup

# Convert geographic names from LCNAF to geonames identifiers.
# Example: Baltimore County (Md.) n79018713
# --> Baltimore County https://www.geonames.org/4347790
# Also builds full hierarchal name: Baltimore County, Maryland, United States

# Some config for requests.
headers = {'User-Agent': 'Custom user agent'}
lc = requests.Session()
ft = requests.Session()
geo = requests.Session()

# Some config for FAST APIs.
labelBase = 'http://id.loc.gov/authorities/names/label/'
ext = '.rdf.xml'
fastURL = 'http://id.worldcat.org/fast/search?query=cql.any+all+%22'
fastPara = '%22&fl=oclc.geographic&recordSchema=info:srw/schema/1/rdf-v2.0'
# Some config for linked data namespaces.
schema = Namespace('http://schema.org/')
gn = Namespace('http://www.geonames.org/ontology#')
mads = Namespace('http://www.loc.gov/mads/rdf/v1#')

all_items = []


def getGraph(url, format, host):
    g = Graph()
    try:
        if host == 'geo':
            data = geo.get(url, timeout=30, headers=headers)
        elif host == 'ft':
            data = ft.get(url, timeout=30, headers=headers)
        elif host == 'lc':
            data = lc.get(url, timeout=30, headers=headers)
        data = data.text
        graph = g.parse(data=data, format=format)
    except requests.exceptions.Timeout:
        graph = None
    return graph


def getlabel(g):
    for s, p, o in g.triples((None, gn.name, None)):
        name = o
        return(name)


def convertLinks(type, url):
    if type == 'sws':
        url = url.replace('s://sws.', '://www.')
        url = url+'about.rdf'
        return url
    else:
        url = url.replace('://www.', 's://sws.')
        url = url.replace('about.rdf', '')
        return url


def findParent(parent):
    url = convertLinks('sws', parent)
    graph = getGraph(url, 'xml', 'geo')
    name = getlabel(graph)
    return name


def addFullName(result):
    name0 = result.get('name0')
    name1 = result.get('name1')
    name2 = result.get('name2')
    if name1 and name2:
        fullName = name0+', '+name1+', '+name2
        result['fullName'] = fullName
    elif name2:
        fullName = name0+', '+name2
        result['fullName'] = fullName
    elif name1:
        fullName = name0+', '+name1
        result['fullName'] = fullName
    else:
        pass


def getParents(parents, result):
    if parents == 'yes':
        if result.get('geoname0'):
            geo = result.get('geoname0')
            # Get linked data for geonames
            gLink = geo+'/about.rdf'
            mgraph = getGraph(gLink, 'xml', 'geo')
            # Find parents
            for s, p, o in mgraph.triples((None, gn.parentADM1, None)):
                parent1 = o
                print(parent1)
                if parent1:
                    name1 = findParent(parent1)
                    result['geoname1'] = parent1.toPython()
                    result['name1'] = name1.value
            for s, p, o in mgraph.triples((None, gn.parentCountry, None)):
                parent2 = o
                print(parent2)
                if parent2:
                    name2 = findParent(parent2)
                    result['geoname2'] = parent2.toPython()
                    result['name2'] = name2.value
            # Create full name
            addFullName(result)
        all_items.append(result)
    else:
        all_items.append(result)


def convertLCNAFToGeoNames(searchTerms, parents):
    all_items.clear()
    for count, result in enumerate(searchTerms):
        # Get results from FAST API
        result = result
        searchTerm = result.get('term')
        print(count, searchTerm)
        searchTerm.rstrip('.')
        url = labelBase+searchTerm
        data = lc.get(url, timeout=30, headers=headers)
        foundName = data.ok
        newURL = data.url
        if foundName:
            newURL = data.url
            newURL = newURL.replace('.html', '')
            graph = getGraph(newURL+'.nt', 'nt', 'lc')
            if graph:
                for s, p, o in graph.triples((None,
                                              mads.hasCloseExternalAuthority,
                                              None)):
                    if 'http://id.worldcat.org/fast/' in o:
                        if result.get('geoname0') is None:
                            # Get linked data of FAST results
                            fastId = o
                            fLink = fastId+ext
                            graph = getGraph(fLink, 'xml', 'ft')
                            if graph:
                                nameAuth = newURL.replace('https', 'http')
                                nameAuth = URIRef(nameAuth)
                                if (None, schema.sameAs, nameAuth) in graph:
                                    objects = graph.objects(subject=None, predicate=schema.sameAs)
                                    for object in objects:
                                        if 'http://www.geonames.org/' in object:
                                            print('hooray')
                                            label = graph.value(subject=object, predicate=RDFS.label)
                                            result['geoname0'] = object
                                            result['name0'] = label
                                            print(object, label)
                                        else:
                                            pass
        # Get parent info from geonames
        getParents(parents, result)
    return all_items


def convertFASTToGeoNames(searchTerms, parents):
    all_items.clear()
    for count, result in enumerate(searchTerms):
        # Get results from FAST API
        result = result
        searchTerm = result.get('term')
        print(count, searchTerm)
        data = ft.get(fastURL+searchTerm+fastPara)
        data = data.content
        soup = Soup(data, features='lxml')
        records = soup.find_all('record')
        for record in records:
            authLabel = record.find('skos:preflabel').string
            if authLabel == searchTerm:
                print('Heading validated')
                altnames = record.find_all('schema:sameas')
                for altname in altnames:
                    uri = altname.find('rdf:description')['rdf:about']
                    label = altname.find('rdfs:label').string
                    if 'http://www.geonames.org/' in uri:
                        print(uri, label)
                        result['geoname0'] = uri
                        result['name0'] = label
            else:
                pass

        # Get parent info from geonames
        getParents(parents, result)
    return all_items
