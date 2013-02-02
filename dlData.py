import os, urllib
from BeautifulSoup import BeautifulStoneSoup

# String to generate below XML file:
# http://api.brain-map.org/api/v2/data/query.xml?criteria=model::SectionDataSet,rma::criteria,products%5Bid$eq5%5D,rma::include,rma::options[num_rows$eq1000],specimen(injections(primary_injection_structure,structure))

soup = BeautifulStoneSoup(open("all-conn.xml").read())

# For each connectivity experiment, we check to see whether it was marked "failed"
for ds in soup.findAll("section-data-set"):
    experimentNumber = int(ds.id.text)
    print experimentNumber
    
    if ds.failed.text == "true":
        print "skipping",  experimentNumber, "marked as failed."
        continue

    newFilePath = os.path.join("rawdata", str(experimentNumber) + ".xpz")

    if os.path.isfile(newFilePath):
        print newFilePath, "already downloaded . . . skipping"
        continue

    url  = '''http://connectivity.brain-map.org/grid_data/v1/visualize/%i?atlas=378''' % experimentNumber
    
    print "Downloading data for experiment:", newFilePath
    urllib.urlretrieve(url, filename=newFilePath)





