from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from mainn import rec_main,dream11
from closer import closer

brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
options = Options()
#options.add_argument("--headless")
options.binary_location = brave_path
options.add_argument("--tor")
driver_path = ChromeDriverManager().install()
driver = webdriver.Chrome(service=Service(driver_path), options=options)
time.sleep(15)
driver.set_page_load_timeout(60)

def extract_player_stats(html_content, div_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    div = soup.find('div', id=div_id)

    if div is None:
        print("Div not found.")
        return

    table = div.find('table')

    if table is None:
        print("Table not found in the div.")
        return

    rows = table.find_all('tr')

    player_stats = []
    title_row = table.find('tr', class_='table-info')
    if title_row is not None:
        title = title_row.find('h2', class_='font-14 text-center')
        if title is not None:
            # if title.text.strip() in previous_i:
            # continue
            print(f"Table Title: {title.text.strip()}")
    for row in rows[1:]:  # Skip the header row
        cols = row.find_all('td')
        stats = [col.text.strip() for col in cols]
        player_stats.append(stats)
        if stats == []:
            player_stats.pop()

    return player_stats
def pitch_stats(b):
    #driver.get(link)
    #time.sleep(5)
    #html_content1 = driver.page_source
    #soup2 = BeautifulSoup(html_content1, 'html.parser')
    #table = soup2.find('table')
    stat0 = []
    #b==table
    #if b == None:
        #return
    rows = b.find_all('tr')
    stats = []
        # Find the table title
    title_row = b.find('tr', class_='table-info')
    if title_row is not None:
        title = title_row.find('h2', class_='font-14 text-center')
        if title is not None:
            #if title.text.strip() in previous_i:
                #return
            print(f"Table Title: {title.text.strip()}")
            #previous_i.append(title.text.strip())
    for row in rows:
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]
            # print(cols)  # Or do something else with the data
        stats.append(cols)
        if cols == []:
            stats.pop()
    return stats

def tablex(driver):
    html_content1 = driver.page_source
    soup2 = BeautifulSoup(html_content1, 'html.parser')
    table = soup2.find_all('table')
    all_cols = []  # Store all cols from all tables
    for c in table:
        if c is None:
            continue
        rows = c.find_all('tr')  # Use c instead of b
        for row in rows:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            all_cols.append(cols)  # Add cols to all_cols
    return all_cols  # Return all_cols
def clean_data(data):
    cleaned_data = []
    for item in data:
        cleaned_item = []
        for element in item:
            cleaned_element = element.replace('▼', '')  # replace '▼' with nothing
            if "\n" in element:
                continue
            cleaned_item.append(cleaned_element)
        cleaned_data.append(cleaned_item)
    return cleaned_data

def suggest_bowlers(data):
    bowler_stats = {}
    data=clean_data(data)
    current_bowler = None
    for i in range(len(data)):
        if len(data[i]) != 7:
            continue
        if len(data[i]) == 7 and 'Stats' in data[i][6]:  # This row contains bowler stats
            current_bowler = data[i][0]
            matches = int(data[i][1])
            #overs = float(data[i][2])
            #avg_runs = float(data[i][3]) if data[i][3] != '' else 0.0
            wickets = int(data[i][4])
            economy = float(data[i][5]) if data[i][5] != '' else 0.0
            total_runs = 0
            total_wickets = 0
            total_economy = 0
        elif len(data[i]) == 7 and r'\n' not in data[i] and current_bowler is not None:
            match_data = data[i]
            try:
                #runs_in_match = int(match_data[3])
                wickets_in_match = int(match_data[4])
                economy_in_match = float(match_data[5]) if match_data[5] != '' else 0.0
            except Exception as e:
                print(f"Error processing row {match_data}: {e}")
                print(type(e).__name__)

            #total_runs += runs_in_match
            total_wickets += wickets_in_match
            total_economy += economy_in_match

            # Calculate the performance score
            performance_score = (4 * total_wickets + 2 * wickets - 0.03 * (total_economy / matches)) / matches

            bowler_stats[current_bowler] = performance_score

    # Sort the bowlers by performance score in descending order
    sorted_bowlers = sorted(bowler_stats.items(), key=lambda item: item[1], reverse=True)

    return sorted_bowlers

def suggest_batsman(data):
    player_stats = {}
    data=clean_data(data)
    current_player = None
    if len(data)<=2:
        pass
    for i in range(len(data)):
        if len(data[i]) != 7:
            continue
        if len(data[i]) == 7 and 'Stats' in data[i][6]:  # This row contains player stats
            current_player = data[i][0]
            matches = int(data[i][1])
            innings = int(data[i][2])
            highest_score = int(data[i][3])
            lowest_score = int(data[i][4])
            try:
                avg_runs = float(data[i][5])
            except ValueError:
                avg_runs = 0
            # Initialize these variables here
            runs = 0
            fours = 0
            sixes = 0
            total_strike_rate = 0
            total_batting_order = 0
        elif len(data[i]) == 7 and r'\n' not in data[i] and current_player is not None:
            match_data = data[i]
            runs_in_match = int(match_data[3].split(' ')[0])
            fours_in_match = int(match_data[4].split('/')[0]) if match_data[4].split('/')[0] != '0.0' else 0
            sixes_in_match = int(match_data[4].split('/')[1])
            strike_rate_in_match = float(match_data[5]) if match_data[5] != '' else 0.0
            batting_order_in_match = int(match_data[2])

            runs += runs_in_match
            fours += fours_in_match
            sixes += sixes_in_match
            total_strike_rate += strike_rate_in_match
            total_batting_order += batting_order_in_match

            # Calculate the performance score
            performance_score = (0.3 * runs + 0.1 * fours + 0.2 * sixes + 0.1 * total_strike_rate + 0.1 * avg_runs + 0.1 * highest_score - 0.05 * lowest_score - 0.05 * (total_batting_order / matches)) / matches

            player_stats[current_player] = performance_score

    # Sort the players by performance score in descending order
    sorted_players = sorted(player_stats.items(), key=lambda item: item[1], reverse=True)

    return sorted_players
def calculate_average_score(matches):
    total_runs = 0
    total_matches = 0
    matches=matches[:-1]
    mcount=0
    sc1=[]
    sc2=[]
    fstWin=0
    for match in matches:
        # Assuming the score is in the format 'runs-wickets (overs)'
        score = match[-2].split('-')[0]
        if matches.index(match)%2==0:
            sc1.append(score)
        else:
            sc2.append(score)
        try:
            total_runs += int(score)
        except ValueError:
            total_runs+=0
        total_matches += 1

    for x,y in zip(sc1,sc2):
        if x=="" or y=="":
            continue
        else:
            mcount+=1
            if int(x)>int(y):
                fstWin+=1
    print(f"first innings win% {(fstWin/mcount)*100}")
    print(f"second innings win% {100-((fstWin / mcount) * 100)}")
    average_score = total_runs / total_matches
    return average_score
def suggest_bowlers_pitch(average_wickets):
    total_avg = sum(average_wickets)
    proportions = [avg / total_avg for avg in average_wickets]
    min_bowlers = [max(0, round(5 * prop)) for prop in proportions]
    max_bowlers = [min(8, round(5 * prop * 1.5)) for prop in proportions]

    # Ensure the total number of bowlers does not exceed 8
    if sum(min_bowlers) > 8:
        min_bowlers = [1 for _ in min_bowlers]
    if sum(max_bowlers) > 8:
        max_bowlers = [2 for _ in max_bowlers]

    return min_bowlers, max_bowlers
def pitch_report(stats):
    total_wickets = [0, 0, 0, 0]
    #print(stats)
    for match in stats:
        if "\n" in match:
            continue
        try:
            for i in range(4):
                total_wickets[i] += int(match[i + 2])
        except ValueError:
            continue

    # Calculate the average wickets
    average_wickets = [total / len(stats) for total in total_wickets]
    return suggest_bowlers_pitch(average_wickets)
# Send a GET request to the webpage
url = 'https://advancecricket.com/upcoming-cricket-matches'
max_attempts = 5
attempts = 0
while attempts < max_attempts:
    try:
        driver.get(url)
        print("Success..")
        break
    except (TimeoutException, WebDriverException) as e:
        print("Error:", type(e).__name__, str(e).split(":")[:5])
        attempts += 1
        print(f"Retrying... ({attempts}/{max_attempts})")

        time.sleep(5)

if attempts == max_attempts:
    print("Failed to load the page after several attempts.")
    driver.quit()
    quit(0)
attempts = 0
main_links={}
while attempts < max_attempts:
    try:
        try:
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, 'flex-fill btn btn-primary btn-sm font-10'))
            WebDriverWait(driver, 45).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        html_content = driver.page_source
        #print(html_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        paragraphs = soup.find_all(class_='flex-fill btn btn-primary btn-sm font-10')
        if not paragraphs:
            raise ValueError("No elements found")
        main_links = {}
        for i in paragraphs:
            href = i['href']
            title = i['title'][:-6]
            main_links.update({title: href})
        if not main_links:
            raise ValueError("main_links is empty")
        break
    except (TimeoutException,WebDriverException,ValueError) as e:
        print("error:", type(e).__name__, str(e).split(":")[:5])
        print("Retrying...")
        attempts += 1
        driver.refresh()
        time.sleep(10)

if attempts == max_attempts:
    print("Failed to find elements after several attempts.")
    driver.quit()
    driver.close()
    exit(0)
    #break
#print(main_links)
match_titles=list(main_links.keys())
match_links=list(main_links.values())
for i in range(len(main_links)):
    print(f"{i}: {match_titles[i]}")
choice=int(input("enter choice:"))
while True:
    try:
        a=driver.get(match_links[choice])
        break
    except TimeoutException:
        print("Retrying..")
        time.sleep(20)

def mlink_get(driver):
    html_content1 = driver.page_source
    soup1 = BeautifulSoup(html_content1, 'html.parser')
    paragraphs = soup1.find_all(class_='dropdown-item')
    stat_link={}
    desired=["Pitch","Dream11","Recent","Batsman","Bowlers"]
    for i in paragraphs:
        href = i['href']
        link_name = i.string
        for x in desired:
            if x in link_name:
                stat_link.update({link_name:href})
                print(f"{link_name}: {href}")
    return stat_link
while True:
    try:
        stat_link=mlink_get(driver)
        if not stat_link:
            raise ValueError
        break
    except ValueError:
        print("Cannot be nill..")
        driver.refresh()
        time.sleep(15)

stat_link.popitem()
stat_link.popitem()
#print(list(stat_link.keys()))
# Extract the data
# This will depend on the structure of the webpage
# For example, if the data is in a table, you might do something like this:
#previous_i = []
newi=list(stat_link.keys())
d11=True
for i in stat_link:
    # print(stat_link[i])
    print()
    print(i)
    driver.get(stat_link[i])
    time.sleep(5)
    html_content1 = driver.page_source
    soup2 = BeautifulSoup(html_content1, 'html.parser')
    table = soup2.find_all('table')
    if table:
        b = table[0]
        rows = b.find_all('tr')
        stats = []
        # Find the table title
        #title_row = b.find('tr', class_='table-info')
        #if title_row is not None:
            #title = title_row.find('h2', class_='font-14 text-center')
            #if title is not None:
                #print(f"Table Title: {title.text.strip()}")
        for row in rows:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            # print(cols)  # Or do something else with the data
            stats.append(cols)
            if cols == []:
                stats.pop()
    else:
        print("No tables found on the page.")

    # stat0=[]
    # for b in table:
    # if b == None:
    # continue
    # print(stats)
    # driver.refresh()
    # time.sleep(5)
    if (i == "Pitch Report" or i == "Pitch Report Bowling"):
        print(table.index(b))
        if table.index(b) == 0 or table.index(b) != 0:
            stats = pitch_stats(table[0])
            print(stats)
            min_bowlers, max_bowlers = pitch_report(stats)
            print("Minimum bowlers to keep: ", min_bowlers)
            print("Maximum bowlers suggested: ", max_bowlers)
            # print("Possible combinations of bowlers: ", combinations)
            total_wickets = [0, 0, 0, 0]
            for match in stats:
                try:
                    for c in range(4):
                        total_wickets[c] += int(match[c + 2])
                except ValueError:
                    continue

            # Calculate the average wickets
            average_wickets = [total / len(stats) for total in total_wickets]

            print('Average wickets taken by each type of bowler:')
            print('Left-arm spinners:', average_wickets[0])
            print('Left-arm fast bowlers:', average_wickets[1])
            print('Right-arm spinners:', average_wickets[2])
            print('Right-arm fast bowlers:', average_wickets[3])
            # driver.quit()
            # break
    if i == "Recent Matches" :
        average_score = calculate_average_score(stats)
        print("Average score in the stadium: ", average_score)
        time.sleep(2)
        #exit(0)
        # break
    if "Batsman" in i:
        driver.refresh()
        time.sleep(15)
        stats = extract_player_stats(driver.page_source, stat_link[i].split("#")[-1])
        top_players = suggest_batsman(stats)
        if top_players != []:
            print("Suggested players to choose from: ", top_players)
        time.sleep(2)
        #exit(0)
        # break
        # print(rows,"\n")
    if "Bowlers" in i:
        driver.refresh()
        time.sleep(15)
        stats = extract_player_stats(driver.page_source, stat_link[i].split("#")[-1])
        top_players = suggest_bowlers(stats)
        if top_players != []:
            print("Suggested players to choose from: ", top_players)
        time.sleep(2)
        #exit(0)
        # break
    if "Recent" in i:
        print(rec_main(driver, stat_link[i]))
        time.sleep(5)
        #exit(0)
        # break
    if "Players Dream11" in i:
            # driver.get(stat_link[i])
        if d11:
            dream11(driver, stat_link[i])
            #exit(0)
        d11 = False
        #print("oombi")
       # break

closer(driver)
