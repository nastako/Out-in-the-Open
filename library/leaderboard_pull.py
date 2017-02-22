import urllib
import requests
import pandas as pd
import sqlite3
import sys, traceback
import time
import random

# Connect to SQLite Database
conn = sqlite3.connect('open_2017.db')
c = conn.cursor()

# Initialize requests
headers = {'Host': 'games.crossfit.com',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}


def make_request(url, params, headers=headers, wait_time=0):
    time.sleep(wait_time)

    response = requests.request("GET", url, headers=headers, params=params)
    response.raise_for_status()  # raise exception if invalid response

    response_json = response.json()
    return response_json


default_score = {1: '--',
                 2: '--',
                 3: '--',
                 4: '--',
                 5: '--',
                 6: '--'}

# Choose parameters
year = 2017
division = 1
scaled = 0
sort = 0
occupation = 0
page = 1
region_num = 0

# divisions = range(2,20)
divisions = [1]
occupations = range(0, 10)
scaleds = [0]

url = "https://games.crossfit.com/competitions/api/v1/competitions/open/2017/leaderboards"

for division in divisions:
    # Loop for every division in divisions list
    print('\n\n**Division: {}'.format(division))

    for scaled in scaleds:
        # Loop for every scaled in scaleds (should only include 0 and/or 1
        print('\n*Scaled: {}'.format(scaled))

        # Make request to find the number of pages
        request_params = {"page": 1, "competition": "1", "year": year, "division": division, "scaled": scaled, "sort": "0",
                       "fittest": "1", "fittest1": region_num, "occupation": occupation}
        response_json = make_request(url, request_params, headers=headers, wait_time=0)
        num_pages = response_json['totalpages']
        pages = range(1, num_pages + 1)

        for page in pages:
            # For each "page"
            request_params['page'] = page

            # Make request for the page of leaderboard info
            response_json = make_request(url, request_params, headers=headers, wait_time=int(random.random() * 3.0))
            current_page = response_json['currentpage']
            print('page {cp} of {tp}'.format(cp=page, tp=num_pages))

            # Extract athlete data from JSON response
            athlete_records = response_json['athletes']
            try:
                for record in athlete_records:
                    athlete_id = record['userid']
                    profile_link = '/athlete/{}'.format(athlete_id)
                    name = record['name']

                    pos = record['overallrank']
                    region = record['region']
                    region_id = record['regionid']
                    affiliate = record['affiliate']
                    affiliate_id = record['affiliateid']
                    age = record['age']
                    height = record['height']
                    weight = record['weight']
                    total_points = record['overallscore']
                    pic = record['profilepic'][2:]
                    div = record['division']
                    scores = record['scores']

                    score = default_score
                    score_rank = default_score
                    score_id = default_score
                    for i, s in enumerate(scores):
                        score[i + 1] = s['workoutresult']
                        score_rank[i + 1] = s['workoutrank']
                        score_id[i + 1] = s['scoreid']

                    # Push data to database
                    row_data = (name, athlete_id, profile_link, pic, region, region_id, div,
                                affiliate, affiliate_id, occupation, scaled, age, height, weight, pos, year,
                                total_points, score[1], score[2], score[3], score[4], score[5], score[6],
                                score_rank[1], score_rank[2], score_rank[3], score_rank[4], score_rank[5],
                                score_rank[6],
                                score_id[1], score_id[2], score_id[3], score_id[4], score_id[5], score_id[6])
                    num_cols = len(row_data)
                    try:
                        c.executemany('''INSERT OR REPLACE INTO leaderboard
                                      VALUES (?{})'''.format(',?' * (num_cols - 1)), [row_data])
                    except sqlite3.Error as e:
                        print "An error occurred (SQLite): ", e.args[0]

            except:
                e = sys.exc_info()
                traceback.print_tb(e[2])
            finally:
                conn.commit()

conn.close()
