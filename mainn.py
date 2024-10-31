import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException

import csv
from collections import defaultdict
import google.generativeai as genai
import time

def quer(frame):
    genai.configure(api_key="AIzaSyDdDpX2sFbSHzkxeyUCOER4Fjccuh-9JwI")
    prompt_parts = [
        rf"from the data frame \n{frame}\n ;predict the expected points for next match and select the best possible players to choose from",
    ]
    #print(prompt_parts)
    response = genai.chat(model="models/chat-bison-001", messages=prompt_parts, temperature=0.9)
    # response = model.generateChat(prompt_parts)
    print(response.last)
    time.sleep(5)
def analyze_stats(file_name):
    stats = defaultdict(list)
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        #next(reader)  # Skip the header
        name = ""
        for row in reader:
            no_vals=0
            try:
                if row:  # Check if row is not empty
                    for i in row:
                        if i =="":
                            no_vals+=1
                    if no_vals>2:
                        continue
                    elif len(row) == 1 and row != [""]:
                        name = row[0].split('-recent')[0]
                    elif row == [""]:
                        continue
                    elif row == ["Date Color = [Green: ODI, Blue: T20, Red: T10, Hundred: Black], Match = ScoreBoard, BO = ting Order, R(B) = Runs(Ball), SR = Strike Rate, OUT = Out Type, O = Overs, R = Runs, m = Maiden, W = Wickets, Eco = Economy'"]:
                        continue
                    elif row[-1] == 'DNB':
                        continue
                    else:
                        if isinstance(row[-1], str):
                            try:
                                try:
                                    economy = float(row[-1])
                                except ValueError:
                                    economy=0
                                wickets = int(row[-2])
                                runs_balls = int(row[-3])
                                overs = float(row[-4])
                                stats[name].append({
                                    'economy': economy,
                                    'wickets': wickets,
                                    'runs_balls': runs_balls,
                                    'overs': overs
                                })
                            except ValueError:
                                batting_order = int(row[2])
                                runs = int(row[3].split("(")[0])
                                try:
                                    balls_faced = int(row[3].split("(")[1].split(")")[0])
                                except ValueError:
                                    balls_faced=0
                                strike_rate = float(row[4]) if row[4] != "" else 0
                                stats[name].append({
                                    'batting_order': batting_order,
                                    'runs': runs,
                                    'balls_faced': balls_faced,
                                    'strike_rate': strike_rate
                                })

            except Exception as e:
                print(f"Error processing row {row}: {e}")
                print(type(e).__name__)
            #print(name)
            #print(stats[name])
    return stats
def tablex(driver):
    html_content1 = driver.page_source
    soup2 = BeautifulSoup(html_content1, 'html.parser')
    tables = soup2.find_all('table')
    all_cols = {}  # Store all cols from all tables in a dict
    current_player = None
    for table in tables:
        if table is None:
            continue
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            # Remove unwanted strings from each string in the list
            cleaned_col = [item.replace("Bat", "").replace("Bowl", "").replace("Loading...", "").replace(r"\n", "").replace(r'Date Color = [Green: ODI, Blue: T20, Red: T10, Hundred: Black], Match = ScoreBoard, BO = ting Order, R(B) = Runs(Ball), SR = Strike Rate,\tOUT = Out Type, O = Overs, R = Runs, m = Maiden, W = Wickets, Eco = Economy',"") for item in cols]
            # If the cleaned list is not empty and does not contain 'Recent Matches', add it to 'all_cols'
            if cleaned_col and 'Recent Matches' not in cleaned_col[0]:
                if len(cleaned_col) >= 2:  # Ensure there are at least two elements
                    # Use the player name, date, and match as the key, and the entire row as the value
                    key = (current_player, cleaned_col[0], cleaned_col[1])
                    all_cols[key] = cleaned_col
    main_list=list(all_cols.values())
    all_rows=[]
    for i in main_list:
        all_rows.append(i)
        if i == r'"Date Color = [Green: ODI, Blue: T20, Red: T10, Hundred: Black], Match = ScoreBoard, BO = ting Order, R(B) = Runs(Ball), SR = Strike Rate, OUT = Out Type, O = Overs, R = Runs, m = Maiden, W = Wickets, Eco = Economy"':
            all_rows.pop()
            return all_rows
    #return  main_list # Return all_cols as a list of values
    return all_rows  # Return all rows
def tableb(driver,name):
    html_content1 = driver.page_source
    soup2 = BeautifulSoup(html_content1, 'html.parser')
    tables = soup2.find_all('table')
    all_cols = []  # Store all cols from all tables in a list
    for table in tables:
        if table is None:
            continue
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            # Remove unwanted strings from each string in the list
            cleaned_col = [item.replace("Bat", "").replace("Bowl", "").replace("Loading...", "").replace(r"\n", "").replace(r'Date Color = [Green: ODI, Blue: T20, Red: T10, Hundred: Black], Match = ScoreBoard, BO = ting Order, R(B) = Runs(Ball), SR = Strike Rate,\tOUT = Out Type, O = Overs, R = Runs, m = Maiden, W = Wickets, Eco = Economy',"") for item in cols]
            # If the cleaned list is not empty and does not contain 'Recent Matches', add it to 'all_cols'
            if cleaned_col and 'Recent' not in cleaned_col[0]:
                # Check if the player's name is in the cleaned data
                if f'{name}' in cleaned_col[0]:
                    # Split the string on newline characters and keep only the part after them
                    cleaned_col[0] = cleaned_col[0].split('\n')[-1]
                    # Remove any remaining empty strings
                    cleaned_col = [item for item in cleaned_col if item]
                all_cols.append(cleaned_col)

    return all_cols

def calculate_performance_score(player_stats):
    total_matches = len(player_stats)
    total_runs = sum(match['runs'] for match in player_stats if 'runs' in match)
    total_wickets = sum(match['wickets'] for match in player_stats if 'wickets' in match)
    total_overs = sum(match['overs'] for match in player_stats if 'overs' in match)
    total_economy = sum(match['economy'] for match in player_stats if 'economy' in match)
    try:
        avg_runs = total_runs / total_matches
        avg_wickets = total_wickets / total_matches
        avg_overs = total_overs / total_matches
        avg_economy = total_economy / total_matches
    except Exception as e:
        print(f"Error processing row {[total_runs ,total_wickets , total_overs , total_economy , total_matches]}: {e}")
        print(type(e).__name__)
        print(player_stats)
        return

    performance_score = avg_runs + 10 * avg_wickets - avg_economy
    return performance_score

def rec_main(driver,url):
    while True:
        try:
            driver.get(url)
        
            accordions = driver.find_elements(By.CLASS_NAME, 'accordion-item')
            break
        except TimeoutException:
            print("Retrying..")
    with open("recent.csv", "w", newline="") as file:
        writer = csv.writer(file)
        bat = []
        bowl = []
        sk1=0
        sk2=0
        #driver.get(url)
        for d in range(len(accordions)):
            while True:
                try:
                    driver.get(url)
                    time.sleep(15)
                    accordions = driver.find_elements(By.CLASS_NAME, 'accordion-item')
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'accordion-item')))
                    accordions = driver.find_elements(By.CLASS_NAME, 'accordion-item')  # Find the accordions again
                    accordion = accordions[d]
                    # Extract the id attribute from the accordion element and print it
                    header_id = accordion.get_attribute('id')
                    #print(f"Header: {header_id}")
                    writer.writerow([f"{header_id}"])
                    writer.writerow([""])
                    pname=header_id.split("-recent")[0]
                    empt=''
                    for i in pname.split("-"):
                        empt+=i.title()
                        empt+=" "
                    empt=empt[:-1]
                    #print(empt)
                    #print(len(empt))
                    try:
                        button = accordion.find_element(By.TAG_NAME, 'button')
                        loading_bar_id = button.get_attribute('data-bs-target').lstrip('#')[8:]
                        while True:
                            try:
                                driver.execute_script("arguments[0].click();", button)
                                WebDriverWait(driver, 3).until_not(
                                    EC.text_to_be_present_in_element((By.ID, f"loadingBar{loading_bar_id}"),
                                                                     'Loading...')
                                )
                                break
                            except ElementClickInterceptedException:
                                print("Retrying Click..")
                                continue
                            except StaleElementReferenceException:
                                print("Stale Element Reference. Relocating the element and retrying...")
                                button = accordion.find_element(By.TAG_NAME, 'button')
                    except NoSuchElementException:
                        print("Button element not found. Check the locator.")

                    try:
                        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'recent-bat-tab')))
                    except TimeoutException:
                        raise TimeoutException
                    #driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    WebDriverWait(driver, 5).until_not(
                        EC.text_to_be_present_in_element((By.ID, f"loadingBar{loading_bar_id}"), 'Loading...')
                    )
                        # Assuming 'element' is the web element containing the href link
                    while True:
                        try:
                            link = element.get_attribute('href')
                            break
                        except UnboundLocalError:
                            WebDriverWait(driver, 25).until_not(
                                EC.text_to_be_present_in_element((By.ID, f"loadingBar{loading_bar_id}"), 'Loading...')
                            )
                    driver.get(link)
                    bat = tableb(driver,empt)
                    #print(f"Batting stats: {bat}")  # Print the batting stats
                    #continue
                    for col in bat:  # Write each row separately
                        if bat.index(col) > sk1:
                            if col==['Date Color = [Green: ODI, Blue: T20, Red: T10, Hundred: Black], Match = ScoreBoard, BO = ting Order, R(B) = Runs(Ball), SR = Strike Rate,\tOUT = Out Type, O = Overs, R = Runs, m = Maiden, W = Wickets, Eco = Economy']:
                                break
                            writer.writerow(col)
                            #print(col)
                            sk1+=1
                    writer.writerow([""])
                    try:
                        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'recent-bowl-tab')))
                    except TimeoutException:
                        raise TimeoutException
                    WebDriverWait(driver, 5).until_not(
                        EC.text_to_be_present_in_element((By.ID, f"loadingBar{loading_bar_id}"), 'Loading...')
                    )
                        # Assuming 'element' is the web element containing the href link
                    link = element.get_attribute('href')
                    driver.get(link)
                    bowl = tablex(driver)
                    for col in bowl:  # Write each row separately
                        if bowl.index(col)>sk2:
                            sk2+=1
                    break

                except TimeoutException:
                    print("retrying")
                    #driver.refresh()
        stats = analyze_stats('recent.csv')
        # Calculate performance scores for each player
        performance_scores = {player: calculate_performance_score(stat) for player, stat in stats.items()}

        return dict(performance_scores)

# Use the function
#stats = analyze_stats('recent.csv')
#for stat in stats:
    #print(stat)
#print(rec_main(driver,"https://advancecricket.com/match/lah-vs-mul-players-recent-matches-match-14-psl-2024/92313242-1#lahore-qalandars-player-matches"))
url="https://advancecricket.com/match/rcb-vs-gg-players-recent-dream11-points-match-5-wpl-2024/31948801-2#royal-challengers-bangalore-women-players-t20-dream11-points"
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def match_ai(df):
    # Create a LinearRegression model
    model = LinearRegression()

    # Initialize an empty list to store the predicted points
    predicted_points = []

    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        # Check if the player has played in the first match
        if pd.notnull(row['M1']):
            # Get the points from the previous matches and reverse the order
            points = row[['M7', 'M6', 'M5', 'M4', 'M3', 'M2', 'M1']].values[::-1].reshape(-1, 1)

            # Train the model on the player's past performance
            model.fit(np.array(range(1, 8)).reshape(-1, 1), points)

            # Predict the points for the next match (M8) for the player
            prediction = model.predict([[8]])[0][0]

            # Ensure that the predicted points are not less than -4
            predicted_points.append(max(prediction, -4))
        else:
            # If the player has not played in the first match, set their predicted points to np.nan
            predicted_points.append(np.nan)

    # Add the predicted points to the DataFrame
    df['Predicted Points M8'] = predicted_points

    print(df[['Player', 'Predicted Points M8']])
    return #df
def dream11(driver,url):
    break_while = False
    #if break_while:  # If the flag is True, break the while loop
        #break
            # Go to the webpage
    while True:
        if break_while:
            break
        # Go to the webpage
        driver.get(url)
        time.sleep(5)
        # Get the HTML of the webpage
        html = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        print(len(tables))

        # If the length of tables is 2, break the loop
        if len(tables) == 2:
            break

        # If not, continue trying
        print("Retrying...")
    count=0
    for tnum in range(len(tables)):
        if count > 1:
            #break_while = True  # Set the flag to True
            break
        count+=1
        print(tnum)
        table = tables[tnum]
                # Find the table
                #table = soup.find('table')

                # Find the table header using the class name
        table_header = driver.find_element(By.CLASS_NAME, 'table-secondary')

                # Extract column names
        column_names = [th.text for th in table_header.find_elements(By.XPATH, './/th')]

                # Get the table rows
        rows = table.find_all('tr')[1:]

                # Get the table data
        data = [[td.text for td in row.find_all('td')] for row in rows]
                # Remove the unwanted line
        data = [line for line in data if "\nPPM = Points Per Match,\tM1= Recent Match,\tMatches 2nd to 7th = [M2,M3,M4,M5,M6,M7]" not in line]
        data.pop(0)
                #print(data)
                #print(column_names)

                # Create a DataFrame
        df = pd.DataFrame(data, columns=column_names)

                # Replace 'NA' with 0
        df.replace('NA', 0, inplace=True)

                # Replace 'NA' with 0
        df.replace('', 0, inplace=True)

                # Then replace NaN values with 0
        df.fillna(0, inplace=True)

                # Print the DataFrame
        print(df)

                # Define the weights for the weighted average
        weights = [7, 6, 5, 4, 3, 2, 1]

                # Convert the data to numeric
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

                # Calculate the average points
        #df['Average Points'] = df.loc[:, 'M1':'M7'].mean(axis=1)
        df['Average Points'] = df['PPM']

                # Calculate the weighted average points
        df['Weighted Points'] = df.loc[:, 'M1':'M7'].apply(lambda row: np.average(row, weights=weights), axis=1)

                # Incorporate PPM into the weighted points
        df['Weighted Points with PPM'] = df['Weighted Points'] * df['PPM']

                # Calculate the standard deviation of the points
        df['Standard Deviation'] = df.loc[:, 'M1':'M7'].std(axis=1)

                # Predict the points for the next match (simple prediction based on average points)
        df['Predicted Points'] = df.loc[:, 'M1':'M7'].mean(axis=1)

                # Suggest the top 3 picks (highest Weighted Points with PPM)
        best_picks = df.nlargest(3, 'Weighted Points with PPM')['Player'].tolist()

                # Players who could play well (above average Weighted Points with PPM)
        potential_players = df[df['Weighted Points with PPM'] > df['Weighted Points with PPM'].mean()][
                    'Player'].tolist()

                # Define a threshold for good performance (you can adjust this as needed)
        good_performance_threshold = df['Average Points'].mean() + df['Average Points'].std()

                # Players with good consistency and good performance
        good_players = df[(df['Weighted Points'] >= df['Weighted Points'].mean()) & (
                            df['Average Points'] >= good_performance_threshold)]['Player'].tolist()

        print(f"Key Players: {good_players}")
        print(f"Top Form players: {best_picks}")
        print(f"Better Form players: {potential_players}")
        #quer(df)
                #print(f"Most Consistent Players: {most_consistent_players}")

                # Print the predicted points for the next match for each player
                #print("\nPredicted Points for Next Match:")
                #for i, row in df.iterrows():
                    #print(f"{row['Player']}: {row['Predicted Points']}")
        match_ai(df)

    break_while=True
    return driver
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# Create your DataFrame
data = {
    'Player': ['A.Capsey', 'A.Sutherland', 'A.Reddy', 'J.Rodrigues', 'J.Jonassen', 'M.Lanning', 'R.Yadav', 'S.Verma', 'S.Pandey', 'T.Bhatia', 'T.Sadhu'],
    'PPM': [48.8, 27.5, 39.1, 31.4, 94.0, 61.0, 50.0, 43.4, 55.2, 17.7, 26.7],
    'M1': [34, 42, 2, 109, 107, 77, 37, 45, 37, 16, 29],
    'M2': [40, 29, 42, 9, 108, 77, 100, 28, 75, 16, 18],
    'M3': [72, 13, 72, 2, 157, 23, 12, 73, 31, 10, 4],
    'M4': [4, 31, 33, 9, 37, 77, 124, 108, 20, 16, 6],
    'M5': [149, 4, 72, 65, 73, 44, 4, 5, 37, 12, 126],
    'M6': [10, 6, 49, 6, 44, 40, 58, 40, 50, 2, 4],
    'M7': [33, 68, 4, 20, 132, 89, 15, 5, 137, 52, 0]
}
#df = pd.DataFrame(data)
#match_ai(df)
