import urllib2
example = urllib2.urlopen("http://example.com").headers.items()
wikipedia = urllib2.urlopen("http://en.wikipedia.org/wiki/Python_(programming_language)").headers.items()
statesman = urllib2.urlopen("http://statesman.com").headers.items()

print([x[1] for x in example if x[0] == 'last-modified'])
print([x[1] for x in statesman if x[0] == 'server'])
print([x[1] for x in wikipedia if x[0] == 'age'])

