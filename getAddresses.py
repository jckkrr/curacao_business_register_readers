# A script to go through the search function of the Curacao business registry record by record to get the address of each business. 
# Recaptcha prevents users from scraping the more detailed records page. 
# However, having the address can give some insight into what is going on.


#####

from bs4 import BeautifulSoup, Tag
import glob
import mechanize
import pandas as pd
import re
import requests
import time

import sys, os
sys.path.append(os.path.abspath('C:\\Users\Jack\Documents\Python_projects\TOOLKIT\scraping_tools'))
import scrapingTools

###########

def getSearch(form_field, field_input):
    
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.open('http://www2.curacao-chamber.cw/companyselect.asp')
    browser.select_form(nr=0)
    
    browser.form[form_field] = field_input

    req = browser.submit()
    byte_text = str(req.read())
    table = re.findall('<table ID="sl" name="sl">.*</tbody></table>', byte_text)[0]
    soup = BeautifulSoup(table, "html.parser")

    columns = [x.text for x in soup.find('thead').contents]
    data = [x.encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8') for x in scrapingTools.getTableBody(soup)[0][0]]
    df = pd.DataFrame(columns=columns)
    df.loc[0] = data
    
    return df

#### 

def getAddress(company_number):
    
    dfA = getSearch('companyid', company_number)
    tradename = dfA.loc[0]['Tradename']
    
    try:
        df = getSearch('name', tradename)
    except:
        df = dfA
        
    return df

#####

def getMultiAddresses(lo, hi):
    
    df = pd.DataFrame()
    
    start_time = time.time()
    
    for n in range(lo, hi):

        print(n, end='\t')
        
        try:
            dfx = getAddress(str(n))    
        except:
            try:
                dfx = getAddress(str(n))    
            except:
                try:
                    dfx = getAddress(str(n))    
                except:
                    time.sleep(10)
                    dfx = getAddress(str(n))
            
        df = pd.concat([df, dfx])
        df = df.reset_index(drop=True)
        df.to_csv(f'CSVs/{lo}_{hi}.csv', index=False)
        
        print(df.shape, end = '\t')
            
        searches_completed = n-lo + 1
        now_time = time.time()
        time_taken = round(now_time-start_time)
        
        avg_search_time = round(time_taken / searches_completed, 2)
        
        print(f'{searches_completed} in {time_taken} secs', end='\t')
        print(f'({avg_search_time} approx avg.)')
        
    

    print('#### COMPLETE ####')
    print()
    input()
    
    return df

### 

print('###### CURACAO BUSINESS REGISTRY SCRAPER #####')
print()

started_files = [int(x.split('_')[0].split('\\')[1]) for x in glob.glob('CSVs/*') if x.split('_')[0].split('\\')[1].isdigit()]

lo = max(started_files) + 100
hi = lo + 99

print(f'Getting address from {lo} to {hi}')

getMultiAddresses(lo, hi)

input()