"""Module containes dictionary _stations, base class Error for custom exceptions and function scraper() for scraping
web-sites of Bureau of Meteorology and test_scraper function wich tests scrpaper function.
More information see in the documentation for Error class, scraper function and test_scraper function."""
import pandas as pd
import requests
import sys
##
class Error(Exception): 
    """Base class for exceptions in this module with suppressed display of chained exceptions.
        The following Errors are inherited from this class:
        InputError -- for arguments' check,
        LocationNotFound -- there is no such location in the corresponding dictionary,
        BomResponceTimedOut -- Responce from BOM server timed out,
        BomConnectionError -- NerworkFailure(e.g. DNS failure, refused connection, etc) for a given number of attempts,
        JSONSchemaError -- Error in the corresponding JSON file
        BomHTTPError -- custom exception for requests' HTTP error thrown if the HTTP request
        returned an unsuccessful status code
        """
    def __init__(self, message):
        Exception.__init__(self, message)
        self.__suppress_context__ = True

class InputError(Error): #class for argument checking
    pass

class LocationNotFound(Error):
    def __init__(self, location_name):
        message = 'Information for location ' + location_name + ' is not found. Exiting...'
        Error.__init__(self, message)

class BomResponceTimedOut(Error):
    def __init__(self, location_name, timeout):
        message = "Request timed out for location {name}. You may think about increasing timeout to greater than "\
                      + "{timeout} seconds. Exiting..."
        message = message.format(name = location_name, timeout = timeout)
        Error.__init__(self, message)

class BomConnectionError(Error):
    def __init__(self, location_name, attempt_num):
        message = "Connection Error for location {name} for {num} attempts."+\
                      ". You may think about increasing number of attempts. Exiting..."
        message = message.format(name = location_name, num = attempt_num)
        Error.__init__(self, message)

class JSONSchemaError(Error):
    pass

class BomHTTPError(Error):
    # custom exception for requests.exceptions.HTTPError
    def __init__(self, url):
        message = "HTTP Error at the address {url} occured. Exiting..."
        message = message.format(url = url)
        Error.__init__(self, message)

# station info
_stations = {    
    'ARCHERFIELD': {'state': 'Q', 'wmo_code': '94575'},\
    'ADELAIDE': {'state': 'S','wmo_code': '94675'},\
    'BANKSTOWN': {'state': 'N', 'wmo_code': '94765'},\
    'MELBOURNE': {'state':'V', 'wmo_code': '95936'}}
    
def scraper(location_name,timeout = 10, attempt_num = 3):
    """Function to do a web-scrape to download and parse
    weather observation data from the BoM.
    Arguments:
        location_name(str or convertible to str) -- station name, can't be an empty string
        timeout(float or convertible to float) -- number of seconds to wait for server
        response, must be greater than 0
        attempt_num(int or convertible to int) -- number of attempts to connect to the BoM server
        in case of Network Failure, must be greater than or equal to 1
    
    Returns:
        pandas.DataFrame object with corresponding weather observations
        indexed by pandas.DateTimeIndex object.

    Raises:
        Custom Exceptions defined in classes inherited from Error class. Check the documentation for this class
    """
    
##  Arguments' check:
    # location_name
    try:
        location_name = str(location_name)
    except ValueError:
        raise InputError("Location_name argument can't be converted to string type. Check the object. Exiting...")
    if(len(location_name)==0):
        raise InputError('Location name MUST NOT be an empty string. Exiting...')
    # timeout
    try:
        timeout = float(timeout)
    except ValueError:
        raise InputError("Timeout argument can't be converted to float type. Check the object. Exiting...")
    if(timeout<=0):
        raise InputError('Timeout MUST be greater than zero')
    # attempt_num
    try:
        attempt_num = int(attempt_num)
    except ValueError:
        raise InputError("Attempt_num argument can't be converted to integer type. Check the object. Exiting...")
    if(attempt_num<1):
        raise InputError('Attempt Number MUST be greater than or equal to 1')

##  url construction
    url = "http://www.bom.gov.au/fwo/ID{state}60901/ID{state}60901.{wmo_code}.json"
    d = _stations.get(location_name.upper())
    if d == None: #station not found
        raise LocationNotFound(location_name)
    url_string = url.format(state=d['state'], wmo_code=d['wmo_code'])
##  catching exceptions for timeout and connection errors
    i_counter = 0
    while True:
        try:
            i_counter = i_counter + 1
            #raise requests.exceptions.ConnectionError
            r = requests.get(url_string, timeout = timeout)
            break
        except (requests.exceptions.Timeout):
            raise BomResponceTimedOut(location_name, timeout)
        except requests.exceptions.ConnectionError:
            if(i_counter<attempt_num):
                print('Connection error for the connection attempt number {0}. Continue...'.format(i_counter))
            else:
                raise BomConnectionError(location_name, attempt_num)
    try: #checking for HTTP Error
        r.raise_for_status()
    except:
        raise BomHTTPError(url_string)
##
    data = r.json()
    key1 =  'observations'
    key2 = 'data'
    try: #catching exception for JSON error
        data = data[key1][key2]
    except KeyError:
        message = "In JSON file at {url} there are no keys '{key1}' or '{key2}'. Check JSON schema. Exiting..."\
                  .format(url = url_string, key1=key1, key2=key2)
        raise JSONSchemaError(message)
    df = pd.DataFrame.from_records(data, index = 'aifstime_utc')
    df.index = pd.to_datetime(df.index)
    return df
##
def test_scraper(location_name='ARCHERFIELD'):
    """Function tests scraper invoked with location_name
        Arguments:
            location name(str)
        Returns:
            bool -- True if scraper's returned value is of type
            pandas.DataFrame and its index is of pandas.DatetimeIndex type
            False -- otherwise"""
    try:
        df = scraper(location_name)
    except:
        print("In function scraper the following error occured.")
        print("{0}:{1}".format(sys.exc_info()[0], sys.exc_info()[1]))
        print("Check the function to find out.")
        return False
    q  = (isinstance(df, pd.DataFrame) and isinstance(df.index, pd.DatetimeIndex))
    if q:
        print('Succes for location '+ str(location_name))
    else:
        print('Something wrong with location '+ str(location_name))
    return q
##
if __name__ == "__main__":
    test_scraper('ARCHERFIELD')
    #df = scraper('ARCHERFIELD')
    #df = scraper(17)
    #df = scraper('')   
    #df = scraper('Moscow')
    #df = scraper('ARCHERFIELD', timeout= 0.001)
    
