import urllib
import pandas as pd
import time
import sqlite3
import sys, traceback
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()
conn = sqlite3.connect('open_2017.db')
c = conn.cursor()


def make_soup(url):
    driver.get(url)
    driver.implicitly_wait(1)
    time.sleep(1)

    soupdata = BeautifulSoup(driver.page_source, 'html.parser')

    return soupdata


default_score = {1: u'--',
                 2: u'--',
                 3: u'--',
                 4: u'--',
                 5: u'--',
                 6: u'--'}

year = 2016
division = 1
scaled = 0
sort = 0
occupation = 0
page = 1
region_num = 0
num_perpage = 100

score_ids = [16.1, 16.2, 16.3, 16.4, 16.5, 16.6]

url_base = 'https://games.crossfit.com/scores/leaderboard.php?'

divisions = [1, 2]
for division in divisions:
    url = "{b}page={p}&division={d}&numberperpage={npp}&competition=0&year=16&scaled={sc}&fittest={r}&occupation={o}".format(
        b=url_base, p=page, d=division, sc=scaled, r=region_num, o=occupation, npp=num_perpage)

    soup = make_soup(url)

    page_buttons = soup.find('div', {'id': 'leaderboard-pager'})
    num_pages = int(page_buttons.findAll('a')[0].contents[0])

    pages = range(1, num_pages + 1)

    for page in pages:
        url = "{b}page={p}&division={d}&numberperpage={npp}&competition=0&year=16&scaled={sc}&fittest={r}&occupation={o}".format(
            b=url_base, p=page, d=division, sc=scaled, r=region_num, o=occupation, npp=num_perpage)
        print('\n***')
        print(url)
        print(page)

        try:
            soup = make_soup(url)

            table = soup.find('table', {'id': 'lbtable'})
            for record in table.findAll('tr')[1:]:
                try:

                    profile_link = record.find('td', {'class': 'name'}).find('a').get('href')
                    athlete_id = int(str(profile_link).split('/')[-1])
                    name = record.find('td', {'class': 'name'}).find('a').contents[0]
                    print(u'Athlete: {a}, {n}'.format(a=athlete_id, n=name))

                    split_number = record.find('td', {'class': 'number'}).contents[0].replace(')', '').split(' (')
                    pos = split_number[0]
                    # info = record.find('ul', {'class': 'info'})
                    # info_vals = info.findAll('li')
                    region = region_num
                    age = ''
                    height = ''
                    weight = ''
                    total_points = split_number[1]
                    scores = record.findAll('span', {'class': 'display'})

                    score = dict(default_score)
                    rank = dict(default_score)
                    for i, s in enumerate(scores):
                        score_split = s.contents[0].replace(u')\n                    ', u'').split(' (')
                        score[i + 1] = score_split[1]
                        rank[i + 1] = score_split[0]

                    row_data = (name, athlete_id, profile_link, region, division,
                                occupation, scaled, age, height, weight, pos, year,
                                total_points, score[1], score[2], score[3], score[4], score[5], score[6],
                                rank[1], rank[2], rank[3], rank[4], rank[5], rank[6],
                                score_ids[0], score_ids[1], score_ids[2], score_ids[3], score_ids[4], score_ids[5])
                    try:
                        c.executemany('''INSERT OR REPLACE INTO leaderboard_16 (athlete_name, athlete_id, athlete_link,
                                        region_id, division, occupation, scaled, age, height, weight, POS, year, total_points,
                                        score1, score2, score3, score4, score5, score6, rank1, rank2, rank3, rank4, rank5, rank6,
                                        score_id1, score_id2, score_id3, score_id4, score_id5, score_id6)
                                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', [row_data])
                    except sqlite3.Error as e:
                        print "An error occurred (SQLite): ", e.args[0]

                    # conn.commit()

                except:
                    e = sys.exc_info()
                    print('Page: {p}'.format(p=page))
                    traceback.print_tb(e[2])

        except:
            e = sys.exc_info()
            traceback.print_tb(e[2])
        finally:
            conn.commit()

driver.close()
conn.close()
