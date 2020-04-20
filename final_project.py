from bs4 import BeautifulSoup
import requests
import json
import secrets
import sqlite3

consumer_key = secrets.API_KEY
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}
conn = sqlite3.connect('COVID-19_507.sqlite')
cur = conn.cursor()

def load_cache(): # called only once, when we run the program
    ''' load the cache file, open it and read it

    Parameters
    ----------
    None

    Returns
    -------
    content in cache
        dic
    '''   
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): # called whenever the cache is changed
    ''' write the content to cache file

    Parameters
    ----------
    cache
        dic:the cache content

    Returns
    -------
    None
    '''  
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()
    return None

def make_url_request_using_cache(url, cache):
    ''' read the chache file to find the content or make url request using url form national park sites and add text of the web page to the cache

    Parameters
    ----------
    url
        str:the url will be reading content from or use to find the content in cache file
    cache
        dic:the cache content

    Returns
    -------
    cache[url]
        str:the content of the url
    '''      
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]     # we already have it, so return it
    else:
        print("Fetching")
        response = requests.get(url) # gotta go get it
        cache[url] = response.text # add the TEXT of the web page to the cache
        save_cache(cache)          # write the cache to disk
        return cache[url]          # return the text, which is now in the cache

def make_url_request_using_cache_json(url, code, cache):
    ''' read the cache file to find the content or make url request using url from API and add json of the web page to the cache

    Parameters
    ----------
    url
        str:the url will be reading content from or use to find the content in cache file
    cache
        dic:the cache content

    Returns
    -------
    cache[url]
        str:the content of the url
    ''' 
    if (url+code in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url+code]     # we already have it, so return it
    else:
        print("Fetching")
        querystring = {"alpha2":code}
        headers = {
            'x-rapidapi-host': "coronavirus-monitor-v2.p.rapidapi.com",
            'x-rapidapi-key': consumer_key
            }
        response = requests.request("GET", url, headers=headers, params=querystring) # gotta go get it
        print(response)
        cache[url+code] = response.json() # add the json of the web page to the cache
        save_cache(cache)          # write the cache to disk
        return cache[url+code]          # return the text, which is now in the cache



CACHE_DICT = load_cache()

def get_country_name_list(first_letter):
    '''user input a letter, get a list of countries which starts from that letter
    Parameters
    ----------
    first_letter
        str: a letter

    return
        list: a list of country number, name, and its population
    '''
    letter=first_letter.lower()
    url="https://www.worldometers.info/geography/alphabetical-list-of-countries/countries-that-start-with-"+letter+"/"
    response = make_url_request_using_cache(url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    table=soup.find(class_="table-responsive")
    countries=[]
    country_list=table.find('tbody').find_all('tr')
    #print (country_list)
    for country in country_list:
        country_infos=country.find_all("td")
        country_num=country_infos[0].text
        country_name=country_infos[1].text
        country_popu = country_infos[2].text
        country_info=country_num+" "+country_name+" "+country_popu
        countries.append(country_info)
    return countries
    #         country_num=country_info[0].text
    # country_popu = country_info[2].text
    # print(country_name)
    # print(country_popu)
    
# return country_names
#print(get_country_name_list("e"))

def get_country_code(country_name):
    '''
    inpute a name, get the country code 

    return
        num: the 2 letter country code
    '''
    name=country_name.lower()
    url="https://countrycode.org/"
    response = make_url_request_using_cache(url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    table=soup.find(class_="table table-hover table-striped main-table")
    country_list=table.find('tbody').find_all('tr')
    #print (country_list)
    for country in country_list:
        country_infos=country.find_all("td")
        if country_infos[0].text.lower() in name:
            country_code_all=country_infos[2].text
            country_code=country_code_all[:2]
            return country_code
        else:
            pass
    
#print(get_country_code("United States"))

def get_country_latest_status(code):
    '''
    inpute a country code, get the country info, and latest status of COVID-19
    
    return
        dic: info and latest status of COVID-19
    '''
    url = "https://coronavirus-monitor-v2.p.rapidapi.com/coronavirus/latest_stat_by_alpha_2_code.php"
    response=make_url_request_using_cache_json(url, code, CACHE_DICT)

    #print(response)
    return response

#print(get_country_latest_status("US"))


def get_country_total_case_history(code):
    '''
    inpute a country code, get the country info, and latest status of COVID-19
    
    return
        dic: info and latest status of COVID-19
    '''
    url = "https://coronavirus-monitor-v2.p.rapidapi.com/coronavirus/history_by_alpha_2.php"
    response=make_url_request_using_cache_json(url, code, CACHE_DICT)
    return response

print(get_country_total_case_history("GB"))

def get_case_VS_population_history():

    pass

def get_total_death_history():
    pass

def get_total_death_VS_population_history():
    pass

def total_recovered_history():
    pass








