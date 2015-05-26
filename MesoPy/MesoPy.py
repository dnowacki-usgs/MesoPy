# ==================================================================================================================== #
# MesoPy                                                                                                               #
# Version: 1.0.2                                                                                                       #
# Copyright (c) 2015 Joshua Clark <jclark754@gmail.com>                                                                #
#                                                                                                                      #
# LICENSE:                                                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated         #
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the  #
# rights to use,copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to       #
# permit persons to whom the Software is furnished to do so, subject to the following conditions:                      #
#                                                                                                                      #
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the #
# Software.                                                                                                            #
#                                                                                                                      #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE #
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS   #
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,WHETHER IN AN ACTION OF CONTRACT, TORT OR   #
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.     #
#                                                                                                                      #
# ==================================================================================================================== #

try:
    import requests

except ImportError:
    raise Exception("MesoPy requires the 'requests' library to work")

# These should NEVER change. Ya blew it if you mess with these.     
token = '3428e1e281164762870915d2ae6781b4'
baseURL = 'http://api.mesowest.net/v2/stations/'

# String values for different types of errors possible. These should be enough to handle the four errors from the API
# and the 3 standard HTTP errors.
connection_error = 'Could not connect to the API. Please check your connection'
timeout_error = 'Connection Timeout, please retry later'
redirect_error = 'Bad URL, check the formatting of your request and try again'
results_error = 'No results were found matching your query'
auth_error = 'The token or API key is not valid, please contact Josh Clark at jclark754@gmail.com to resolve this'
rule_error = 'This request violates a rule of the API. Please check the guidelines for formatting a data request ' + \
             'and try again'
catch_error = 'Something went wrong. Check all your calls and try again'

# ==================================================================================================================== #
# MesoPyError class                                                                                                    #
# Type: Exception                                                                                                      #
# Description: This class is simply the means for error handling when an exception is raised. Takes in the above       #
# listed error variables                                                                                               #
# ==================================================================================================================== #


class MesoPyError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message

    def __str__(self):
        """ This just returns one of the above error messages """
        return repr(self.error_message)


# ==================================================================================================================== #
# Functions:                                                                                                           #
# ==================================================================================================================== #


def checkresponse(response):
    """ Returns the data requested by the other methods assuming
    the response from the API is ok. If not, provides error
    handling for all possible API errors. HTTP errors are
    handled in the other methods.

    Args:
        None
    Returns:
        response as a dictionary
    Raises:
        resultsError if response is 2
        authError if response is 200
        ruleError if response is 400
        formatError if response is -1
        catchError if response is other

    """

    if response['SUMMARY']['RESPONSE_CODE'] == 1:
        return response
    elif response['SUMMARY']['RESPONSE_CODE'] == 2:
        raise MesoPyError(results_error)
    elif response['SUMMARY']['RESPONSE_CODE'] == 200:
        raise MesoPyError(auth_error)
    elif response['SUMMARY']['RESPONSE_CODE'] == 400:
        raise MesoPyError(rule_error)
    elif response['SUMMARY']['RESPONSE_CODE'] == -1:
        format_error = response['SUMMARY']['RESPONSE_MESSAGE']
        raise MesoPyError(format_error)
    else:
        raise MesoPyError(catch_error)


def latest_obs(stid, token=token, **kwargs):
    """ Returns in JSON format latest observations at a user
    specified location for a specified time. Other parameters
    may also be included (see above). See the station_list
    method for station IDs.

    Args:
    The following parameters are MANDATORY
        stid: Single or comma separated list of MesoWest station IDs e.g. stid=kden,kslc,wbb

    The following parameters are OPTIONAL
        attime: Date and time in form of YYYYMMDDhhmm for which returned obs are closest. All times are UTC.
            e.g. attime=201504261800
        within: When used without 'attime', it can be left blank to return the latest ob or represent the number of
            minutes which would return the latest ob within that time period. When used with 'attime' it can be a single
            number representing a time period before attime or two comma separated numbers representing a period before
            and after the attime e.g. attime=201306011800&within=30,30 would return the ob closest to attime within a 30
            minute period before or after attime.
        obtimezone: Set to either UTC or local. Sets timezone of obs. Default is UTC. e.g. obtimezone=local
        showemptystations: Set to '1' to show stations even if no obs exist that match the time period. Stations without
            obs are omitted by default.
        state: US state, 2-letter ID e.g. state=CO
        country: Single or comma separated list of abbreviated 2 or 3 character countries e.g. country=us,ca,mx
        county: County/parish/borough (US/Canada only), full name e.g. county=Larimer
        radius: Distance from a lat/lon pt as [lat,lon,radius (mi)]e.g. radius=-120,40,20
        bbox: Stations within a [lon/lat] box in the order [lonmin,latmin,lonmax,latmax] e.g. bbox=-120,40,-119,41
        cwa: NWS county warning area (string) e.g. cwa=LOX See http://www.nws.noaa.gov/organization.php for CWA list
        nwsfirezone: NWS Fire Zone (string) e.g. nwsfirezone=LOX241
        gacc: Name of Geographic Area Coordination Center e.g. gacc=EBCC See http://gacc.nifc.gov/ for a list of GACC
            abbreviations
        subgacc: Name of Sub GACC e.g. subgacc=EB07
        vars: single or comma separatd list of sensor variables. Will return all stations that match one of provided
            variables. Useful for filtering all stations that sense only certain vars. Do not request vars twice in the
            query. e.g. vars=wind_speed,pressure Use the variables method to see a list of sensor vars
        status: A value of either active or inactive returns stations currently set as active or inactive in the
            archive. Omitting this param returns all stations e.g. status=active
        units: string or set of strings and by pipes separated by commas. Default is metric units. Set units=ENGLISH for
            FREEDOM UNITS ;) Valid  other combinations are as follows: temp|C, temp|F, temp|K; speed|mps, speed|mph,
            speed|kph, speed|kts; pres|pa, pres|mb; height|m, height|ft; precip|mm, precip|cm, precip|in; alti|pa,
            alti|inhg. e.g. units=temp|F,speed|kph,metric
        groupby: Results can be grouped by key words: state, county, country, cwa, nwszone, mwsfirezone, gacc, subgacc
            e.g. groupby=state
    Returns:
        a dictionary of latest time observations
    Raises:
        connection_error if no internet connection
        timeout_error if a request takes longer than anticipated
        redirect_error if the request is redirected too many times
    """

    latest_url = 'nearesttime?&' + 'stid=' + stid + '&' + '&'.join(['%s=%s' % (key, value) for (key, value) in
                                                                    kwargs.items()]) + '&token=' + token

    try:
        resp = requests.get(baseURL + latest_url)
        data = resp.json()
    except requests.exceptions.ConnectionError:
        raise MesoPyError(connection_error)
    except requests.exceptions.Timeout:
        raise MesoPyError(timeout_error)
    except requests.exceptions.TooManyRedirects:
        raise MesoPyError(redirect_error)
    except requests.exceptions.RequestException as e:
        raise e
    return checkresponse(data)


def precipitation_obs(stid, start, end, token=token, **kwargs):
    """ Returns in JSON a time series of observations at a user
    specified location for a specified time. Other parameters
    may also be included (see above). See the station_list
    method for station IDs.

    Args:
    The following parameters are MANDATORY
        stid: Single or comma separated list of MesoWest station IDs. e.g. stid=kden,kslc,wbb
        start: Start date in form of YYYYMMDDhhmm. MUST BE USED WITH THE END PARAMETER. Default time is UTC
            e.g., start=201306011800
        end: End date in form of YYYYMMDDhhmm. MUST BE USED WITH THE START PARAMETER. Default time is UTC
            e.g., end=201306011800

    The following parameters are OPTIONAL
        obtimezone: Set to either UTC or local. Sets timezone of obs. Default is UTC. e.g. obtimezone=local
        showemptystations: Set to '1' to show stations even if no obs exist that match the time period. Stations without
            obs are omitted by default.
        state: US state, 2-letter ID e.g. state=CO
        country: Single or comma separated list of abbreviated 2 or 3 character countries e.g. country=us,ca,mx
        county: County/parish/borough (US/Canada only), full name e.g. county=Larimer
        radius: Distance from a lat/lon pt as [lat,lon,radius (mi)]e.g. radius=-120,40,20
        bbox: Stations within a [lon/lat] box in the order [lonmin,latmin,lonmax,latmax] e.g. bbox=-120,40,-119,41
        cwa: NWS county warning area (string) e.g. cwa=LOX See http://www.nws.noaa.gov/organization.php for CWA list
        nwsfirezone: NWS Fire Zone (string) e.g. nwsfirezone=LOX241
        gacc: Name of Geographic Area Coordination Center e.g. gacc=EBCC See http://gacc.nifc.gov/ for a list of GACC
            abbreviations
        subgacc: Name of Sub GACC e.g. subgacc=EB07
        vars: single or comma separatd list of sensor variables. Will return all stations that match one of provided
            variables. Useful for filtering all stations that sense only certain vars. Do not request vars twice in the
            query. e.g. vars=wind_speed,pressure Use the variables method to see a list of sensor vars
        status: A value of either active or inactive returns stations currently set as active or inactive in the
            archive. Omitting this param returns all stations e.g. status=active
        units: string or set of strings and by pipes separated by commas. Default is metric units. Set units=ENGLISH for
            FREEDOM UNITS ;) Valid  other combinations are as follows: temp|C, temp|F, temp|K; speed|mps, speed|mph,
            speed|kph, speed|kts; pres|pa, pres|mb; height|m, height|ft; precip|mm, precip|cm, precip|in; alti|pa,
            alti|inhg. e.g. units=temp|F,speed|kph,metric
        groupby: Results can be grouped by key words: state, county, country, cwa, nwszone, mwsfirezone, gacc, subgacc
            e.g. groupby=state
    Returns:
        a dictionary of precipitation observations
    Raises:
        connection_error if no internet connection
        timeout_error if a request takes longer than anticipated
        redirect_error if the request is redirected too many times
    """

    precip_url = 'precipitation?' + '&stid=' + stid + '&start=' + start + '&end=' + end + '&' + \
                 '&'.join(['%s=%s' % (key, value) for (key, value) in kwargs.items()]) + '&token=' + token

    try:
        resp = requests.get(baseURL + precip_url)
        data = resp.json()
    except requests.exceptions.ConnectionError:
        raise MesoPyError(connection_error)
    except requests.exceptions.Timeout:
        raise MesoPyError(timeout_error)
    except requests.exceptions.TooManyRedirects:
        raise MesoPyError(redirect_error)
    except requests.exceptions.RequestException as e:
        raise e
    return checkresponse(data)


def timeseries_obs(stid, start, end, token=token, **kwargs):
    """ Returns in JSON a time series of observations at a user
    specified location for a specified time. Other parameters
    may also be included (see above). See the station_list
    method for station IDs.

    Args:
    The following parameters are MANDATORY
        stid: Single or comma separated list of MesoWest station IDs. e.g. stid=kden,kslc,wbb
        start: Start date in form of YYYYMMDDhhmm. MUST BE USED WITH THE END PARAMETER. Default time is UTC
            e.g., start=201306011800
        end: End date in form of YYYYMMDDhhmm. MUST BE USED WITH THE START PARAMETER. Default time is UTC
            e.g., end=201306011800

    The following paramters are OPTIONAL
        output: Changes the output to csv or JSON format if requesting a single station time series. Default is JSON
            unless requested time series is longer than two years e.g. output=csv
        obtimezone: Set to either UTC or local. Sets timezone of obs. Default is UTC. e.g. obtimezone=local
        showemptystations: Set to '1' to show stations even if no obs exist that match the time period. Stations without
            obs are omitted by default.
        state: US state, 2-letter ID e.g. state=CO
        country: Single or comma separated list of abbreviated 2 or 3 character countries e.g. country=us,ca,mx
        county: County/parish/borough (US/Canada only), full name e.g. county=Larimer
        radius: Distance from a lat/lon pt as [lat,lon,radius (mi)] e.g. radius=-120,40,20
        bbox: Stations within a [lon/lat] box in the order [lonmin,latmin,lonmax,latmax] e.g. bbox=-120,40,-119,41
        cwa: NWS county warning area (string) e.g. cwa=LOX See http://www.nws.noaa.gov/organization.php for CWA list
        nwsfirezone: NWS Fire Zone (string) e.g. nwsfirezone=LOX241
        gacc: Name of Geographic Area Coordination Center e.g. gacc=EBCC See http://gacc.nifc.gov/ for a list of GACC
            abbreviations
        subgacc: Name of Sub GACC e.g. subgacc=EB07
        vars: single or comma separated list of sensor variables. Will return all stations that match one of provided
            variables. Useful for filtering all stations that sense only certain vars. Do not request vars twice in the
            query. e.g. vars=wind_speed,pressure Use the variables method to see a list of sensor vars
        status: A value of either active or inactive returns stations currently set as active or inactive in the archive
            Omitting this param returns all stations e.g. status=active
        units: string or set of strings and by pipes separated by commas. Default is metric units. Set units=ENGLISH for
            FREEDOM UNITS ;) Valid  other combinations are as follows: temp|C, temp|F, temp|K; speed|mps, speed|mph,
            speed|kph, speed|kts; pres|pa, pres|mb; height|m, height|ft; precip|mm, precip|cm, precip|in; alti|pa,
            alti|inhg. e.g. units=temp|F,speed|kph,metric
        groupby: Results can be grouped by key words: state, county, country, cwa, nwszone, mwsfirezone, gacc, subgacc
            e.g. groupby=state
    Returns:
        a dictionary of time series observations
    Raises:
        connection_error if no internet connection
        timeout_error if a request takes longer than anticipated
        redirect_error if the request is redirected too many times
    """

    timeseries_url = 'timeseries?' + '&stid=' + stid + '&start=' + start + '&end=' + end + '&' + \
                     '&'.join(['%s=%s' % (key, value) for (key, value) in kwargs.items()]) + '&token=' + token

    try:
        resp = requests.get(baseURL + timeseries_url)
        data = resp.json()
    except requests.exceptions.ConnectionError:
        raise MesoPyError(connection_error)
    except requests.exceptions.Timeout:
        raise MesoPyError(timeout_error)
    except requests.exceptions.TooManyRedirects:
        raise MesoPyError(redirect_error)
    except requests.exceptions.RequestException as e:
        raise e
    return checkresponse(data)


def climatology_obs(stid, startclim, endclim, token=token, **kwargs):
    """ Returns in JSON a time series of observations at a user specified location for a specified time. Other
    parameters may also be included (see above). See the station_list method for station IDs.

    Args:
    The following parameters are MANDATORY
        stid: Single or comma separated list of MesoWest station IDs. e.g. stid=kden,kslc,wbb
        startclim: Start date in form of MMDDhhmm. MUST BE USED WITH THE ENDCLIM PARAMETER. Default time is UTC
            e.g. startclim=06011800 Do not specify a year
        endclim: End date in form of MMDDhhmm. MUST BE USED WITH THE STARTCLIM PARAMETER. Default time is UTC
            e.g. endclim=06011800 Do not specify a year

    The following parameters are OPTIONAL
        output: Changes the output to csv or JSON format if requesting a single station time series. Default is JSON
            unless requested time series is longer than two years e.g. output=csv
        obtimezone: Set to either UTC or local. Sets timezone of obs. Default is UTC. e.g. obtimezone=local
        showemptystations: Set to '1' to show stations even if no obs exist that match the time period. Stations
            without obs are omitted by default.
        state: US state, 2-letter ID e.g. state=CO
        country: Single or comma separated list of abbreviated 2 or 3 character countries e.g. country=us,ca,mx
        county: County/parish/borough (US/Canada only), full name e.g. county=Larimer
        radius: Distance from a lat/lon pt as [lat,lon,radius (mi)] e.g. radius=-120,40,20
        bbox: Stations within a [lon/lat] box in the order [lonmin,latmin,lonmax,latmax] e.g. bbox=-120,40,-119,41
        cwa: NWS county warning area (string) e.g. cwa=LOX See http://www.nws.noaa.gov/organization.php for CWA list
        nwsfirezone: NWS Fire Zone (string) e.g. nwsfirezone=LOX241
        gacc: Name of Geographic Area Coordination Center e.g. gacc=EBCC See http://gacc.nifc.gov/ for a list of GACC
            abbreviations
        subgacc: Name of Sub GACC e.g. subgacc=EB07
        vars: single or comma separated list of sensor variables. Will return all stations that match one of provided
            variables. Useful for filtering all stations that sense only certain vars. Do not request vars twice in the
            query. e.g. vars=wind_speed,pressure Use the variables method to see a list of sensor vars
        status: A value of either active or inactive returns stations currently set as active or inactive in the
            archive. Omitting this param returns all stations e.g. status=active
        units: string or set of strings and by pipes separated by commas. Default is metric units. Set units=ENGLISH
            for FREEDOM UNITS ;) Valid  other combinations are as follows: temp|C, temp|F, temp|K; speed|mps, speed|mph,
            speed|kph, speed|kts; pres|pa, pres|mb; height|m, height|ft; precip|mm, precip|cm, precip|in; alti|pa,
            alti|inhg. e.g. units=temp|F,speed|kph,metric
        groupby: Results can be grouped by key words: state, county, country, cwa, nwszone, mwsfirezone, gacc, subgacc
            e.g. groupby=state
    Returns:
        a dictionary of climatology observations
    Raises:
        connection_error if no internet connection
        timeout_error if a request takes longer than anticipated
        redirect_error if the request is redirected too many times
    """

    climatology_url = 'climatology?' + '&stid=' + stid + '&startclim=' + startclim + '&endclim=' + endclim + '&' \
                      + '&'.join(['%s=%s' % (key, value) for (key, value) in kwargs.items()]) + '&token=' \
                      + token

    try:
        resp = requests.get(baseURL + climatology_url)
        data = resp.json()
    except requests.exceptions.ConnectionError:
        raise MesoPyError(connection_error)
    except requests.exceptions.Timeout:
        raise MesoPyError(timeout_error)
    except requests.exceptions.TooManyRedirects:
        raise MesoPyError(redirect_error)
    except requests.exceptions.RequestException as e:
        raise e
    return checkresponse(data)


def station_list(**kwargs):
    """ Returns in JSON format a list of stations (and metadata)that corresponds to user-specified parameters.

    Args:
    The user may pass in any of the below parameters as string arguments
        state: US state, 2-letter ID e.g. state=CO
        county: County/parish/borough (US/Canada only), full name e.g. county=Larimer
        radius: Distance from a lat/lon pt as [lat,lon,radius (mi)] e.g. radius=-120,40,20
        bbox: Stations within a [lon/lat] box in the order [lonmin,latmin,lonmax,latmax] e.g. bbox=-120,40,-119,41
        cwa: NWS county warning area (string) e.g. cwa=LOX See http://www.nws.noaa.gov/organization.php for CWA list
        nwsfirezone: NWS Fire Zone (string) e.g. nwsfirezone=LOX241
        gacc: Name of Geographic Area Coordination Center e.g. gacc=EBCC See http://gacc.nifc.gov/ for a list of GACC
            abbreviations
        subgacc: Name of Sub GACC e.g. subgacc=EB07
    Returns:
        dictionary of requested stations
    Raises:
        connection_error if no internet connection
        timeout_error if a request takes longer than anticipated
        redirect_error if the request is redirected too many times
    """

    station_url = 'metadata?network=1,2&' + '&'.join(['%s=%s' % (key, value) for (key, value) in kwargs.items()]) \
                  + '&token=' + token

    try:
        resp = requests.get(baseURL + station_url)
        data = resp.json()
    except requests.exceptions.ConnectionError:
        raise MesoPyError(connection_error)
    except requests.exceptions.Timeout:
        raise MesoPyError(timeout_error)
    except requests.exceptions.TooManyRedirects:
        raise MesoPyError(redirect_error)
    except requests.exceptions.RequestException as e:
        raise e
    return checkresponse(data)


def variable_list():
    """ Returns in JSON format a list of variables that could be obtained from the 'vars' param in other functions. Some
    stations may not record all variables listed. Use the station_list function to return metadata on each station.

    Args:
        None
    Returns:
        dictionary of station variables
    Raises:
        connection_error if no internet connection
        timeout_error if a request takes longer than anticipated
        redirect_error if the request is redirected too many times
    """
    variable_url = 'http://api.mesowest.net/v2/variables?' + '&token=' + token

    try:
        resp = requests.get(variable_url)
        data = resp.json()
    except requests.exceptions.ConnectionError:
        raise MesoPyError(connection_error)
    except requests.exceptions.Timeout:
        raise MesoPyError(timeout_error)
    except requests.exceptions.TooManyRedirects:
        raise MesoPyError(redirect_error)
    except requests.exceptions.RequestException as e:
        raise e
    return checkresponse(data)
