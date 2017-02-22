import pandas as pd
import numpy as np
import sqlite3
import time
from pandas.io import sql as pd_sql


def convert_numeric(df, cols=None):
    if cols == None:
        cols = df.columns
    for c in cols:
        try:
            df[c].replace('NA', None)
            df[c] = pd.to_numeric(df[c], errors='coerce')
            # print('Successfully converted {} to numeric'.format(c))
        except:
            print('Could not convert {} to numeric'.format(c))
    return df


def read_old_leaderboard(division='all', stages='all'):
    conn = sqlite3.connect('open_2017.db')

    if division == 'all':
        where_division = ""
    else:
        where_division = "WHERE division = {}".format(division)

    if stages == 'all':
        query = "SELECT * FROM leaderboard_old {}".format(where_division)
    elif type(stages) is list:
        cols_stage = '`{}`' + ', `{}`' * (len(stages) - 1)
        cols_stage = cols_stage.format(*stages)
        query = "SELECT athlete_id, division, {s} FROM leaderboard_old {w}".format(w=where_division, s=cols_stage)
    elif type(stages) is str:
        where_stage = 'WHERE stage = `{}`'.format(stages)
    else:
        query = "SELECT * FROM leaderboard_old {}".format(where_division)

    leaderboard_df = pd.read_sql_query(query, conn, coerce_float=True)

    conn.close()

    return leaderboard_df


def read_new_leaderboard(division='all', stages='all'):
    conn = sqlite3.connect('open_2017.db')

    if division == 'all':
        where_division = ""
    else:
        where_division = "WHERE division = {}".format(division)

    if stages == 'all':
        query = "SELECT * FROM leaderboard_new {}".format(where_division)
    elif type(stages) is list:
        cols_stage = '`{}`' + ', `{}`' * (len(stages) - 1)
        cols_stage = cols_stage.format(*stages)
        cols_scaled = '`{}_scaled`' + ', `{}_scaled`' * (len(stages) - 1)
        cols_scaled = cols_scaled.format(*stages)
        query = "SELECT athlete_id, division, {s}, {sc} FROM leaderboard_new {w}".format(w=where_division, s=cols_stage,
                                                                                         sc=cols_scaled)
    elif type(stages) is str:
        query = "SELECT athlete_id, division, {s}, {sc} FROM leaderboard_new {d}".format(s=stages,
                                                                                         sc=stages + '_scaled',
                                                                                         d=where_division)
    else:
        query = "SELECT * FROM leaderboard_new {}".format(where_division)

    leaderboard_df = pd.read_sql_query(query, conn, coerce_float=True)

    conn.close()

    return leaderboard_df


def get_old_athlete(athlete_id):
    conn = sqlite3.connect('open_2017.db')

    where_athlete = "WHERE athlete_id = {}".format(athlete_id)

    query = "SELECT * FROM athletes_old {}".format(where_athlete)

    athletes_df = pd.read_sql_query(query, conn, coerce_float=True)

    conn.close()

    return athletes_df


def get_old_athletes(division='all'):
    conn = sqlite3.connect('open_2017.db')

    if division == 'all':
        where_division = ""
    else:
        division = [2, 1][division]
        where_division = "WHERE gender_num = {}".format(division)

    query = "SELECT * FROM athletes_old {}".format(where_division)

    athletes_df = pd.read_sql_query(query, conn, coerce_float=True)

    conn.close()

    return athletes_df


def get_results_old(division='all', stages='all'):
    leaderboard_df = read_old_leaderboard(division, stages)
    athletes_df = get_old_athletes(division)
    results_df = pd.merge(leaderboard_df.reset_index(), athletes_df, on='athlete_id', how='left')

    return results_df


def get_results_new(division='all', stages='all'):
    leaderboard_df = read_new_leaderboard(division, stages)
    athletes_df = get_old_athletes(division)
    results_df = pd.merge(leaderboard_df.reset_index(), athletes_df, on='athlete_id', how='left')

    return results_df

# results_df = get_results_old(division=1, stages=[14.1, '15.1'])
# print(results_df.head())
