from bs4 import BeautifulSoup
import requests
import json
import secrets
import sqlite3
import plotly.graph_objects as go 

consumer_key = secrets.API_KEY
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}
DB_NAME = 'COVID-19_507.sqlite'

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
    ''' read the chache file to find the content or make url request using url form of the website sites and add text of the web page to the cache

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
        print("Fetching, this may take a while")
        querystring = {"alpha2":code}
        headers = {
            'x-rapidapi-host': "coronavirus-monitor-v2.p.rapidapi.com",
            'x-rapidapi-key': consumer_key
            }
        response = requests.request("GET", url, headers=headers, params=querystring).json() # gotta go get it
        #print(response)
        infos=list(response.values())[1]
        # print(infos)
        # print(type(infos))
        #print(response)
        # info_list=list(infos.reverse())
        # print(info_list)
        # print(type(info_list))
        # info_list = []
        # j = 0
        # print(len(infos))
        filtered_info=[]
        date=None
        for i in range(len(infos) - 1, -1 , -1):
            info = infos[i]
            # print(info)
            new_date=info["record_date"][0:10]
            # print(new_date)
            if new_date == date:
                pass
            else: 
                date = new_date
                # print(date)
                filtered_info.append(info)
        
        # print(filtered_info[::-1])
                
        cache[url+code] = filtered_info[::-1] # add the json of the web page to the cache
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
        country_popu_str=country_infos[2].text
        country_popu = country_popu_str.replace(',', '')
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
#print(get_country_total_case_history("GB"))

def create_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    #drop_country_info_sql='DROP TABLE IF EXISTS "Country_info"'
    #drop_history_sql = 'DROP TABLE IF EXISTS "Status_history"'

    create_country_info_sql = '''
        CREATE TABLE IF NOT EXISTS "Country_info" (
            "Country_code"	TEXT NOT NULL,
            "Country_name"	TEXT NOT NULL,
            "Population" INTEGER NOT NULL,
            PRIMARY KEY("Country_code")
        )
    '''
    
    create_history_sql = '''
        CREATE TABLE IF NOT EXISTS "Status_history" (
            "Country_code"	TEXT NOT NULL,
            "Time" TEXT NOT NULL,
            "Total_cases" INTEGER,
            "Total_deaths" INTEGER,
            "Active_cases" INTEGER,
            "Total_recovered" INTEGER,
            "Tot_case_pop_perc"	REAL,
            "Tot_death_pop_perc" REAL,
            "Actv_case_pop_perc" REAL,
            PRIMARY KEY("Country_code","Time")
            FOREIGN KEY("Country_code")
                REFERENCES Country_info("Country_code") 
        )
    '''
    #cur.execute(drop_country_info_sql)
    #cur.execute(drop_history_sql)
    cur.execute(create_country_info_sql)
    cur.execute(create_history_sql)
    conn.commit()
    conn.close()

def add_country_info_sqlite(country_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    insert_country_info_sql = '''
        INSERT INTO Country_info 
        VALUES (?,?,?)
    ''' 

    update_sql = '''
    update Country_info 
    set population = ?
    where country_code=?
    '''

    country_code = get_country_code(country_name)
    first_letter=country_name[0]
    country_list=get_country_name_list(first_letter)
    country_population = None

    for item in country_list:
        if country_name in item:
            country_population = int(item.split()[-1])
    
    try:
        cur.execute(insert_country_info_sql, [country_code, country_name, country_population])
    except:
        cur.execute(update_sql, [country_population, country_code])

    
    conn.commit()
    conn.close()  



def add_history_sqlite(country_name):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    insert_history_sql = '''
        INSERT INTO Status_history 
        VALUES (?,?,?,?,?,?,?,?,?)
    '''    

    update_sql = '''
    update Status_history 
    set Total_cases =?,
        Total_deaths=?,
        Active_cases =?,
        Total_recovered=?,
        Tot_case_pop_perc=?,
        Tot_death_pop_perc=?,
        Actv_case_pop_perc = ?
    where country_code=? and
        time = ?'''


    country_code = get_country_code(country_name)
    get_population='''
        SELECT Population
        FROM Country_info
        WHERE Country_code = ?
    '''

    cur.execute(get_population,[country_code])
    result = cur.fetchone()
    population=int(list(result)[0])

    country_records=get_country_total_case_history(country_code)
    for record in country_records:
        total_cases=0
        active_cases=0
        total_deaths=0
        total_recovered = 0
        if str(record.get("total_cases"))=='':
            total_cases=0
        else:
            total_cases=int(str(record.get("total_cases")).replace(',', ''))

        if str(record.get("active_cases"))=='':
            active_cases=0
        else:
            active_cases=int(str(record.get("active_cases")).replace(',', ''))

        if str(record.get("total_deaths"))=='':
            total_deaths=0
        else:
            total_deaths=int(str(record.get("total_deaths")).replace(',', ''))
        
        if str(record.get("total_recovered"))=='':
            total_deaths=0        
        elif str(record.get("total_recovered")) == "N/A" :
            total_recovered = total_cases - total_deaths - active_cases
        else :
            total_recovered = int(str(record.get("total_recovered")).replace(',', ''))
        # print(total_recovered)
        
        tot_case_pop_perc=(float(total_cases)/population)*100
        tot_death_pop_perc=(float(total_deaths)/population)*100
        actv_case_pop_perc=(float(active_cases)/population)*100
        time=record.get("record_date")[0:10]
        
        try:
            cur.execute(insert_history_sql, [
            country_code,
            time,
            total_cases,
            total_deaths,
            active_cases,
            total_recovered,
            tot_case_pop_perc,
            tot_death_pop_perc,
            actv_case_pop_perc
            ])
        except: 
            cur.execute(update_sql, [
            total_cases,
            total_deaths,
            active_cases,
            total_recovered,
            tot_case_pop_perc,
            tot_death_pop_perc,
            actv_case_pop_perc,
            country_code,
            time
            ])

    conn.commit()
    conn.close()  

def get_all_date(country_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    total_case='''
    SELECT Time
    FROM Status_history
    WHERE Country_code = ?
    '''
    cur.execute(total_case,[country_code])
    result = list(cur.fetchall())
    res = []
    for item in result:
        res.append(list(item)[0][0:10])
    #print(res)
    conn.commit()
    conn.close()  
    return res

def get_total_cases_data (country_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    total_case='''
    SELECT Total_cases
    FROM Status_history
    WHERE Country_code = ?
    '''
    cur.execute(total_case,[country_code])
    result = list(cur.fetchall())
    res = []
    for item in result:
        res.append(list(item)[0])
    #print(res)
    conn.commit()
    conn.close()  
    return res


def get_totl_case_pop_data (country_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    total_case='''
    SELECT Tot_case_pop_perc
    FROM Status_history
    WHERE Country_code = ?
    '''
    cur.execute(total_case,[country_code])
    result = list(cur.fetchall())
    res = []
    for item in result:
        res.append(list(item)[0])
    #print(res)
    conn.commit()
    conn.close()  
    return res

def get_total_deaths_data (country_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    total_case='''
    SELECT Total_deaths
    FROM Status_history
    WHERE Country_code = ?
    '''
    cur.execute(total_case,[country_code])
    result = list(cur.fetchall())
    res = []
    for item in result:
        res.append(list(item)[0])
    #print(res)
    conn.commit()
    conn.close()  
    return res

def get_totl_deaths_pop_data (country_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    total_case='''
    SELECT Tot_death_pop_perc
    FROM Status_history
    WHERE Country_code = ?
    '''
    cur.execute(total_case,[country_code])
    result = list(cur.fetchall())
    res = []
    for item in result:
        res.append(list(item)[0])
    #print(res)
    conn.commit()
    conn.close()  
    return res

def get_active_cases_data (country_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    total_case='''
    SELECT Active_cases
    FROM Status_history
    WHERE Country_code = ?
    '''
    cur.execute(total_case,[country_code])
    result = list(cur.fetchall())
    res = []
    for item in result:
        res.append(list(item)[0])
    #print(res)
    conn.commit()
    conn.close()  
    return res

def get_activ_case_pop_data (country_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    total_case='''
    SELECT Actv_case_pop_perc
    FROM Status_history
    WHERE Country_code = ?
    '''
    cur.execute(total_case,[country_code])
    result = list(cur.fetchall())
    res = []
    for item in result:
        res.append(list(item)[0])
    #print(res)
    conn.commit()
    conn.close()  
    return res

def get_total_recovered_data (country_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    total_case='''
    SELECT Total_recovered
    FROM Status_history
    WHERE Country_code = ?
    '''
    cur.execute(total_case,[country_code])
    result = list(cur.fetchall())
    res = []
    for item in result:
        res.append(list(item)[0])
    #print(res)
    conn.commit()
    conn.close()  
    return res


if __name__ == "__main__":
    # state_dic=build_state_url_dict()
    # state_names=state_dic.keys()
    graphic_list=["[1] Total case history", "[2] Total case/population history", "[3] Total death history", "[4] Total death/population history", "[5] Total active history", "[6] Total active/population history","[7] Total recovered history"]
    status=True
    while status:
        user_input=input("Enter an initial letter (e.g. A) or 'exit': ")
        if user_input =="exit":
            print ("Please stay safe and healthy. Bye~")
            break
        elif not (user_input.isalpha()):
            print ("[Error] Please enter a letter")
        elif len(user_input)!= 1:
            print("[Error] Please only enter one letter")
        else:
            
            while True:
                countries=get_country_name_list(user_input.lower())
                print("-"*20)
                print("List of countries start with " + user_input)
                print("-"*20)
                # number=0
                # for item in state_instance:
                #     number+=1
                #     print ("["+str(number)+"] "+item.info())
                for name in countries:
                    country_num=name.split()[0]
                    other_info = name.split()[1:-1]
                    country_name = ""
                    for info in other_info:
                        if country_name == "":
                            country_name += info
                        else:
                            country_name += (" " + info)
                    print (country_num+" "+country_name)
                print()
                print()
                new_input=input("Choose the number for current status or 'exit' or 'back': ")
                
                if new_input=="exit":
                    print("Please stay safe and healthy. Bye~")
                    status=False
                    break
                elif new_input=="back":
                    print()
                    break
                elif not (new_input.isnumeric()):
                    print ("[Error] Invalid input, please enter a number")
                elif int(new_input)> len(countries):
                    print("[Error] Invalid input, please enter a number between 1-"+str(len(countries)))
                    
                else:
                    country=countries[int(new_input)-1]
                    print("-"*20)
                    country_code=get_country_code(country)
                    country_latest_status=get_country_latest_status(country_code)
                    total_cases=country_latest_status[0].get("total_cases")
                    new_cases=country_latest_status[0].get("new_cases")
                    active_cases=country_latest_status[0].get("active_cases")
                    total_deaths=country_latest_status[0].get("total_deaths")
                    new_deaths=country_latest_status[0].get("new_deaths")
                    total_recovered=0
                    if country_latest_status[0].get("total_recovered")=="N/A":
                        total_recovered = int(total_cases.replace(',', '')) - int(total_deaths.replace(',', '')) - int(active_cases.replace(',', ''))
                    else :
                        total_recovered = country_latest_status[0].get("total_recovered")
                    record_date=country_latest_status[0].get("record_date")[1:10]

                    print()
                    other_info = country.split()[1:-1]
                    country_name = ""
                    for info in other_info:
                        if country_name == "":
                            country_name += info
                        else:
                            country_name += (" " + info)
                    print()
                    print("Current status of " + country_name)
                    print("Total cases: "+ total_cases)
                    print("New cases: "+ new_cases)
                    print("Active cases: "+ active_cases)
                    print()
                    print("Total deaths: "+ total_deaths)
                    print("New deaths: "+ new_deaths)
                    print()
                    print("Total recovered: "+ str(total_recovered))
                    print()
                    print("Update time: "+ record_date)

                    print("-"*20)      
                    print()
                    for item in graphic_list:
                        print (item)
                    print()

                    while True:
                        graph_input=input("Choose the number for graphics you want to see or 'back': ")
                        # if graph_input=="exit":
                        #     print("Bye~")
                        #     status=False
                        #     break
                        if graph_input=="back":
                            print()
                            break
                        elif not (graph_input.isnumeric()):
                            print ("[Error] Invalid input, please enter a number")
                        elif int(graph_input)> len(graphic_list):
                            print("[Error] Invalid input, please enter a number between 1-"+str(len(graphic_list)))
                            #new_input=input("Choose the number for detail search or'exit'or'back': ")
                            
                        else:
                            create_db()
                            add_country_info_sqlite(country_name)
                            add_history_sqlite(country_name)
                            xvals=get_all_date(country_code)
                            #data_type=[Total_cases,Total_deaths"]
                            name=str()
                            if graph_input== "1":
                                yvals=get_total_cases_data(country_code)
                                name="Total cases history of "
                            elif graph_input== "2":
                                yvals=get_totl_case_pop_data(country_code)
                                name="Total cases over population (in %) history of "
                            elif graph_input== "3":
                                yvals=get_total_deaths_data(country_code)
                                name="Total deaths history of "
                            elif graph_input== "4":
                                yvals=get_totl_deaths_pop_data(country_code)
                                name="Total deaths population (in %) history of "
                            elif graph_input== "5":
                                yvals=get_active_cases_data(country_code)
                                name="Active cases history of "
                            elif graph_input== "6":
                                yvals=get_activ_case_pop_data(country_code)
                                name="Active cases population (in %) history of "
                            elif graph_input== "7":
                                yvals=get_total_recovered_data(country_code)
                                name="Total recovered history of "
                                                   
                            scatter_data = go.Scatter(x=xvals, y=yvals, mode='lines+markers')
                            basic_layout = go.Layout(title=name + country_name)
                            fig = go.Figure(data=scatter_data, layout=basic_layout)
                            fig.write_html("scatter.html", auto_open=True)








