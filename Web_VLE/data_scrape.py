from urllib.request import urlopen
from bs4 import BeautifulSoup

# Getting Compound Data from NIST Webbook
def antoineParameters(compound):
    link = "https://webbook.nist.gov/cgi/cbook.cgi?Name=" + compound + "&Units=SI"
    page = urlopen(link).read()
    soup = BeautifulSoup(page, features="html.parser")

    # Finds CAS registry number for compound listed
    strCAS = '' #initialize
    allLi = soup.find_all('li')
    for i in range(0, len(allLi)):
        if ("CAS Registry Number:" in allLi[i].text):
            strCAS = allLi[i].text
            break
    if strCAS == '':
        raise AntoineError(compound)
    numCAShyphen = strCAS[21:]  # Removes "CAS Registry Number: " from string
    numCAS = numCAShyphen.replace('-', '')  # Removes hyphens from number

    # Thermo Phase change data
    url = "https://webbook.nist.gov/cgi/cbook.cgi?ID=C" + numCAS + "&Units=SI&Mask=4#Thermo-Phase"
    htmlText = urlopen(url).read()
    soup = BeautifulSoup(htmlText, features="html.parser")
    try:
        Trange = []
        for i in soup.find_all("tr", {"class": "exp"}):
            if ('Antoine Equation Parameters' in i.parent.attrs.values()):
                children = i.findChildren('td')
                tabulatedVal = []
                for j in range(0, len(children)):
                    if (children[j].text[0].isalpha() == False):
                        tabulatedVal.append(children[j].text)
                Trange.append(tabulatedVal)
        if Trange == []:
            raise AntoineError(compound)
        else:
            return Trange
    except AntoineError as e:
        e.__str__()
        # messagebox.showwarning('Error', e)

# Get Boiling Point Data from NIST
def boilPoint(compound):
    link = "https://webbook.nist.gov/cgi/cbook.cgi?Name=" + compound + "&Units=SI"
    page = urlopen(link).read()
    soup = BeautifulSoup(page, features="html.parser")

    # Finds CAS registry number for compound listed
    strCAS = ''  # initialize
    allLi = soup.find_all('li')
    for i in range(0, len(allLi)):
        if ("CAS Registry Number:" in allLi[i].text):
            strCAS = allLi[i].text
            break
    if strCAS == '':
        raise BoilPointError(compound)
    numCAShyphen = strCAS[21:]  # Removes "CAS Registry Number: " from string
    numCAS = numCAShyphen.replace('-', '')  # Removes hyphens from number

    # Thermo Phase change data
    url = "https://webbook.nist.gov/cgi/cbook.cgi?ID=C" + numCAS + "&Units=SI&Mask=4#Thermo-Phase"
    htmlText = urlopen(url).read()
    soup = BeautifulSoup(htmlText, features="html.parser")

    boilT = 0.0
    try:
        for i in soup.find_all("tr", {"class": "cal"}):
            if ('One dimensional data' in i.parent.attrs.values()):
                children = i.findChildren('td')
                for j in range(0, len(children)):
                    if (children[j].text == "Tboil"):
                        if (children[j + 1].text[0].isalpha() == False):
                            boilAll = children[j + 1].text
                            if (" ± " in boilAll):
                                boilT = boilAll.split(" ± ")[0]
                            else:
                                boilT = boilAll
        if boilT == 0:
            for i in soup.find_all("tr", {"class": "exp"}):
                if 'One dimensional data' in i.parent.attrs.values():
                    children = i.findChildren('td')
                    for j in range(0, len(children)):
                        if children[j].text == "Tboil":
                            if children[j + 1].text[0].isalpha() == False:
                                boilAll = children[j + 1].text
                                if " ± " in boilAll:
                                    boilT = boilAll.split(" ± ")[0]
                                else:
                                    boilT = boilAll
            if boilT == 0:
                raise BoilPointError(compound)
            else:
                return boilT
        else:
            return boilT
    except BoilPointError as e:
        e.__str__()
        # messagebox.showwarning('Error', e)


# Custom Errors
class AntoineError(Exception):
    """ Error raised when an problem occurs in web scrapping for Antoine Equation data
    Attributes:

    """

    def __init__(self, compound):
        self.compound = compound

    def __str__(self):
        message = 'No Antoine Parameter Data Found for the Following Compound: '
        return 'No Antoine Parameter Data Found for the compound: {}'.format(self.compound)


class BoilPointError(Exception):
    """ Error raised if the boiling point of a compound can't be found ## is this needed anymore?
    Attributes:
        Compound -- Which Compound caused the error
    """

    def __init__(self, compound):
        self.compound = compound

    def __str__(self): # add color to user inputs
        message = 'The Boiling Point for the Following Compound Could Not Be Found: '
        return 'The Boiling Point for {} Could Not Be Found'.format(self.compound)
