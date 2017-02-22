import urllib
import pandas as pd
import time
import sqlite3
import sys, traceback
import re
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


def convert2pounds(weight_str):
    if 'lb' in weight_str:
        weight_lbs = float(weight_str.split(' ')[0])
    elif 'kg' in weight_str:
        weight_lbs = 2.2 * float(weight_str.split(' ')[0])
    else:
        weight_lbs = None

    return weight_lbs


def convert2cm(height_str):
    if 'cm' in height_str:
        height_cm = float(height_str.split(' ')[0])
    elif "'" in height_str:
        split_height = height_str.split("'")
        feet = int(split_height[0])
        inches_part = int(split_height[1][:-1])
        inches = feet * 12 + inches_part
        height_cm = inches * 2.54
    else:
        height_cm = None

    return height_cm


def convert2sec(time_str):
    if ":" in time_str:
        time_split = time_str.split(':')
        minutes = int(time_split[0])
        seconds_part = int(time_split[1])
        seconds = minutes * 60 + seconds_part
    else:
        seconds = None

    return seconds


def clean_val(val_str):
    if "--" in val_str:
        clean_value = None
    else:
        try:
            clean_value = int(val_str)
        except:
            clean_value = None

    return clean_value


stats_dict_default = {'Deadlift': '',
                      'Back Squat': '',
                      'Clean and Jerk': '',
                      'Snatch': '',
                      'Fight Gone Bad': '',
                      'Max Pull-ups': '',
                      'Fran': '',
                      'Grace': '',
                      'Helen': '',
                      'Filthy 50': '',
                      'Sprint 400m': '',
                      'Run 5k': ''}

url_base = 'https://games.crossfit.com/athlete/'

athletes = conn.execute("""SELECT athlete_id, athlete_link, pic, region_name, region_id, division, age, height, weight,
                            affiliate, affiliate_id, athlete_name
                            FROM leaderboard ORDER BY athlete_id ASC""")
athletes = athletes.fetchall()
#36538

for i, athlete in enumerate(athletes):
    try:
        athlete_dict = dict(
            athlete_id=athlete[0],
            athlete_link=athlete[1],
            pic=athlete[2],
            region_name=athlete[3],
            region_id=athlete[4],
            division=athlete[5],
            age=athlete[6],
            height=athlete[7],
            weight=athlete[8],
            affiliate=athlete[9],
            affiliate_id=athlete[10],
            athlete_name=athlete[11])

        print((i, athlete_dict['athlete_link'], athlete_dict['athlete_name']))

        url = '{b}{id}'.format(b=url_base, id=athlete_dict['athlete_id'])
        soup = make_soup(url)

        try:
            info_bar = soup.find('ul', {'class': 'infobar'})
            info_items = info_bar.findAll('div', {'class': 'text'})

            athlete_dict['division_name'] = re.sub(r"(\w)([A-Z])", r"\1 \2",
                                                   info_items[1].contents[0].replace(u'\n', u'').replace(u' ', u''))
            athlete_dict['team'] = info_items[6].find('a').contents[0]
            athlete_dict['team_link'] = info_items[6].find('a').get('href')
            athlete_dict['team_id'] = athlete_dict['team_link'].split('/')[2]
        except:
            pass

        try:
            athlete_dict['affiliate_link'] = info_items[5].find('a').get('href')
        except:
            pass

        stats_dict = dict(stats_dict_default)
        try:
            athlete_profile = soup.find('div', {'id': 'athleteProfile'})
            stats_tables = athlete_profile.findAll('table', {'class': 'stats'})

            for stats_table in stats_tables:
                stats = stats_table.findAll('tr')
                for stat in stats:
                    stat_name = stat.find('th').contents[0][1:-1]
                    stat_val = stat.find('td').contents[0][1:]
                    if not ((stat_val == u'') or (stat_name == u'')):
                        if (stat_val[-1] == u' ') or (stat_val[-1] == ' '):
                            stat_val = stat_val[:-1]
                        stats_dict[stat_name] = stat_val
        except:
            pass

        athlete_dict['back_squat_lb'] = convert2pounds(stats_dict['Back Squat'])
        athlete_dict['deadlift_lb'] = convert2pounds(stats_dict['Deadlift'])
        athlete_dict['clean_and_jerk_lb'] = convert2pounds(stats_dict['Clean and Jerk'])
        athlete_dict['snatch_lb'] = convert2pounds(stats_dict['Snatch'])
        athlete_dict['weight_lb'] = convert2pounds(athlete_dict['weight'])
        try:
            athlete_dict['weight_kg'] = athlete_dict['weight_lb'] / 2.2
        except:
            athlete_dict['weight_kg'] = None

        athlete_dict['height_cm'] = convert2cm(athlete_dict['height'])
        try:
            athlete_dict['height_in'] = athlete_dict['height_cm'] / 2.54
        except:
            athlete_dict['height_in'] = None

        athlete_dict['fran'] = convert2sec(stats_dict['Fran'])
        athlete_dict['grace'] = convert2sec(stats_dict['Grace'])
        athlete_dict['helen'] = convert2sec(stats_dict['Helen'])
        athlete_dict['filthy_50'] = convert2sec(stats_dict['Filthy 50'])
        athlete_dict['sprint_400m'] = convert2sec(stats_dict['Sprint 400m'])
        athlete_dict['run_5k'] = convert2sec(stats_dict['Run 5k'])

        athlete_dict['pull_ups'] = clean_val(stats_dict['Max Pull-ups'])
        athlete_dict['fight_gone_bad'] = clean_val(stats_dict['Fight Gone Bad'])

        columns = ', '.join(athlete_dict.keys())
        placeholders = ', '.join('?' * len(athlete_dict))
        query = 'INSERT OR REPLACE INTO athletes ({}) VALUES ({})'.format(columns, placeholders)
        c.execute(query, athlete_dict.values())
    except KeyboardInterrupt:
        raise
    except:
        e = sys.exc_info()
        traceback.print_tb(e[2])
    finally:
        if i % 10 == 0:
            conn.commit()

conn.commit()
driver.close()
conn.close()
