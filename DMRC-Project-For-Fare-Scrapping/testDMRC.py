
import json
from bs4 import BeautifulSoup
import requests
import re
import csv
from robobrowser import RoboBrowser


class DMRC ( ):

    def getStationNames ( self , list , startSplitSymbol , endSplitSymbol ):
        finalString = ""
        for data in list:
            line = str ( data )
            if line != '\n':
                finalString = finalString + self.getStationCodes ( line )
                endIndex = line.rfind ( endSplitSymbol )
                startIndex = line.find ( startSplitSymbol )
                for var in range ( (startIndex + 1) , (endIndex) ):
                    finalString = finalString + line[ var ]
            finalString = finalString + ','
        return finalString

    def getStationCodes ( self , line ):
        codeStr = ""
        endIndex = line.rfind ( '"' )
        startIndex = line.find ( '"' )
        for var in range ( (startIndex + 1) , (endIndex) ):
            codeStr = codeStr + line[ var ]
        return codeStr + "="


def initiate ( url="http://www.delhimetrorail.com/metro-fares.aspx" ):
    return requests.get ( url )


def getListOfStationsWithStationCodes ():
    page = initiate ( )
    obj = DMRC ( )
    l = [ ]
    soup = BeautifulSoup ( page.content , 'html.parser' )
    ref = soup.find ( 'select' , attrs={'class': 'slt_stnr mrgn'} )
    var = obj.getStationNames ( ref , startSplitSymbol=">" , endSplitSymbol="</" ).split ( "," )
    for d in var:
        if d != '':
            l.append ( d )
    return l


def getStationDict ( l ):
    SD = {}
    ctr = 0
    for data in l:
        key = data.split ( "=" )
        if len ( key ) == 2:
            SD.update ( {key[ 0 ]: key[ 1 ]} )
        else:
            print ( 'Skipping the index that has inconsistent data at Inex {}'.format ( ctr ) )
        ctr = ctr + 1
    return SD


def getStationFare ( fro , to , url ):
    br = RoboBrowser ( history=True , parser="html.parser" )
    br.open ( url )
    form = br.get_form ( )
    form[ 'ctl00$MainContent$ddlFrom' ].value = str ( fro )
    form[ 'ctl00$MainContent$ddlTo' ].value = str ( to )
    br.submit_form ( form )
    src = str ( br.parsed ( ) )
    return src

def writeToFile (filepath='DMRC-Fare.csv', finaldata=[] ):
    with open ( filepath,"a") as f:
        writer = csv.writer ( f )
        writer.writerow(finaldata)



def writedicttofile(var):
    # as requested in comment
    with open ( 'Satation-file.txt' , 'w' ) as file:
        file.write ( json.dumps ( var ) )


if __name__ == '__main__':
    header=['Form station' ,'To station' ,'Normal Fare' ,'Concessional Fare','Time' ,'Number of Stations' ,'Interchange']
    lstto = [ ]
    lstfrom = [ ]
    StationData = {}
    lstfromStationCode = getListOfStationsWithStationCodes ( );
    StationData = getStationDict ( lstfromStationCode )
    writedicttofile(StationData)
    for stationcodes in StationData.keys ( ):
        lstto.append ( stationcodes )
        lstfrom.append ( stationcodes )
    print ( "Header Written To FIle" , writeToFile ( finaldata=header ) )
    writeToFile ( filepath="stationfrom.csv" ,finaldata=lstto)
    writeToFile ( filepath="stationfrom.csv",finaldata=lstfrom )
    for src in lstfrom:
        for dest in lstto:
            finaldata = [ ]
            finaldata.append ( src )
            finaldata.append ( dest )
            r = getStationFare ( src , dest , "http://www.delhimetrorail.com/metro-fares.aspx" )
            data = r
            soup = BeautifulSoup ( data , "html.parser" )
            data = soup.find ( class_="fare_new_nor_right" )
            finaldata.append(data.text) # print ( data.text)
            data = soup.find ( class_="fare_new_right_right" )
            finaldata.append(data.text) #print ( data
            data1 = soup.find_all ( class_="fr_sect1" )
            soup2 = BeautifulSoup ( str ( data1 ) , "html.parser" )
            ctr = 0;
            for lists in soup2.find_all ( 'li' ):
                finaldata.append(lists.text)
               # print ( "d",lists.text )
                if ctr >= 2:
                    break
                ctr += 1
            print("Wrote It To FIle {}",writeToFile(finaldata=finaldata))



