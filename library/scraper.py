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
    driver.implicitly_wait(3)
    time.sleep(3)

    soupdata = BeautifulSoup(driver.page_source, 'html.parser')

    return soupdata


default_score = {1: u'--(--)',
                 2: u'--(--)',
                 3: u'--(--)',
                 4: u'--(--)',
                 5: u'--(--)',
                 6: u'--(--)'}

year = 2017
division = 1
scaled = 0
sort = 0
occupation = 0
page = 1
region_num = 0

url_base = 'https://games.crossfit.com/leaderboard?&competition=1'

divisions = [1]
for division in divisions:
    url = '{b}&page={p}&year={y}&division={d}&scaled={sc}&sort={s}&fittest1={r}5&occupation={o}'.format(
        b=url_base, p=page, y=year, d=division, sc=scaled, s=sort, r=region_num, o=occupation)
    soup = make_soup(url)

    num_pages = int(soup.find('div', {'class': 'pages'}).findAll('a')[-1].contents[0])
    print(num_pages)

    pages = range(1, num_pages+1)

    for page in pages:
        url = '{b}&page={p}&year={y}&division={d}&scaled={sc}&sort={s}&fittest1={r}5&occupation={o}'.format(
            b=url_base, p=page, y=year, d=division, sc=scaled, s=sort, r=region_num, o=occupation)
        print('\n***')
        print(url)

        try:
            soup = make_soup(url)

            table = soup.find('table')
            for record in table.findAll('tr')[1:]:
                try:
                    profile_link = record.find('a', {'class': 'profile-link'}).get('href')
                    athlete_id = int(str(profile_link).split('/')[-1])
                    name = record.find('div', {'class': 'full-name'}).contents[0]
                    print(u'Athlete: {a}, {n}'.format(a=athlete_id, n=name))

                    pos = record.find('td', {'class': 'pos'}).contents[0]
                    info = record.find('ul', {'class': 'info'})
                    info_vals = info.findAll('li')
                    region = info_vals[0].contents[0]
                    age = info_vals[1].contents[0]
                    height = info_vals[2].contents[0]
                    weight = info_vals[3].contents[0]
                    total_points = record.find('td', {'class': 'total-points'}).contents[0]
                    scores = record.findAll('div', {'class': 'rank-result'})

                    score = default_score
                    for i, s in enumerate(scores):
                        score[i + 1] = s.contents[0]

                    row_data = (name, athlete_id, profile_link, region, division,
                                occupation, scaled, age, height, weight, pos, year,
                                total_points, score[1], score[2], score[3], score[4], score[5], score[6])

                    try:
                        c.executemany('''INSERT OR REPLACE INTO leaderboard
                                      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', [row_data])
                    except sqlite3.Error as e:
                        print "An error occurred (SQLite): ", e.args[0]

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
