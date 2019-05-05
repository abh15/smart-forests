# -*- coding: utf-8 -*-
"""
This code takes temperature and humidity data from ruuvitag and calculates hyperlocalized Fire Weather Index(FWI) 

Uses libfwi, a modified version of pyfwi library (https://github.com/buckinha/pyfwi)

"""
import libfwi
import time
from influxdb import InfluxDBClient
from prettyprinter import pprint
my_dict={}
new_dic={}
roovi_macs=("F91E573C41F8","CFFC1D652E98","F8A7DB587E2D","F0E9505C25A4","F47B8890C50A","F26D5323ED83") #Roovi tag macs
roovi_locs={"F91E573C41F8":"Tjallmo","CFFC1D652E98":"Hastveda","F8A7DB587E2D":"Gnosjo","F0E9505C25A4":"Ljusdal","F47B8890C50A":"Norrkoping","F26D5323ED83":"Ronneby"} #roovi_tag simulated locations
def getfwi(t_stamp,humidity,temp):
    fwi=libfwi.calcFWI(5,temp,humidity,10,0,85,6,15,60.20)  # Calulate FWI data assuming some constants
    #(month, temperature, relative humidity, wind speed, rain, previous FFMC, DMC, DC, and latitude)
    return fwi

def main(host='10.84.109.148', port=8086):
    """Instantiate a connection to the InfluxDB."""
    user = ""
    password = ""
    dbname = "ruuvi1"
    dbuser = ""
    dbuser_password = ""
    client = InfluxDBClient(host, port, user, password, dbname)
    for mac in roovi_macs:
       query = "select last(humidity),temperature, time from ruuvi_measurements where mac = "+"\'"+mac+"\'" #filter temp, humidity data across all ruuvitags
       result = client.query(query)
       cpu_points = list(result.get_points(measurement='ruuvi_measurements'))   #convert datatype to list
       for points in cpu_points:
           val= getfwi(points.get('time'),points.get('last'),points.get('temperature'))
           new_dic[roovi_locs.get(mac)]=val     #store FWI index acc to location
    print(" \n\n\tLocation    |\t FWI")
    pprint (new_dic)


if __name__ == '__main__':
   while True:
       time.sleep(5)   #Run the code after every 5 seconds
       main()
