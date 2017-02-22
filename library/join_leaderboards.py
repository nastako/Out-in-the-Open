import pandas as pd
import numpy as np
import sqlite3
from pandas.io import sql as pd_sql


def convert2sec(time_str):
    if ":" in time_str:
        time_split = time_str.split(':')
        minutes = int(time_split[0])
        seconds_part = int(time_split[1])
        seconds = minutes * 60 + seconds_part
    else:
        seconds = None

    return seconds


def extract_scaled_score(s):
    try:
        ss = s.split(')')[0]
    except AttributeError:
        ss = s

    return ss


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


def create_leaderboard_old():
    # Load Data
    conn = sqlite3.connect('open_2017.db')
    leaderboard_16_df = pd.read_sql_query("SELECT * FROM leaderboard_16", conn, coerce_float=True)
    leaderboard_15_df = pd.read_sql_query("SELECT * FROM leaderboard_15", conn, coerce_float=True)
    leaderboard_14_df = pd.read_sql_query("SELECT * FROM leaderboard_14", conn, coerce_float=True)
    leaderboard_13_df = pd.read_sql_query("SELECT * FROM leaderboard_13", conn, coerce_float=True)

    # Clean 2016 Data

    first_row16 = leaderboard_16_df.loc[0]
    score_col = {
        'score1': float(first_row16['score_id1']),
        'score2': float(first_row16['score_id2']),
        'score3': float(first_row16['score_id3']),
        'score4': float(first_row16['score_id4']),
        'score5': float(first_row16['score_id5']),
        'score6': float(first_row16['score_id6'])
    }
    for key, value in score_col.iteritems():
        fltr = leaderboard_16_df[key].str.contains('s')
        leaderboard_16_df[str(value) + '_scaled'] = 0
        leaderboard_16_df.loc[fltr, str(value) + '_scaled'] = 1
        leaderboard_16_df[key] = leaderboard_16_df[key].apply(extract_scaled_score)
        if key == 'score5':
            leaderboard_16_df[key] = leaderboard_16_df[key].apply(convert2sec)

        leaderboard_16_df[key] = pd.to_numeric(leaderboard_16_df[key], errors='coerce')

    lb16_pivot = leaderboard_16_df[
        ['athlete_id', 'division', 'score1', 'score2', 'score3', 'score4', 'score5', 'score6',
         str(score_col['score1']) + '_scaled', str(score_col['score2']) + '_scaled',
         str(score_col['score3']) + '_scaled', str(score_col['score4']) + '_scaled',
         str(score_col['score5']) + '_scaled', str(score_col['score6']) + '_scaled']]
    lb16_pivot.rename(columns=score_col, inplace=True)

    # Convert values to numeric 13-15
    leaderboard_num_cols = [u'year', u'division', u'stage', u'athlete_id', u'rank', u'score', u'scaled']

    leaderboard_15_df = convert_numeric(leaderboard_15_df, leaderboard_num_cols)
    leaderboard_14_df = convert_numeric(leaderboard_14_df, leaderboard_num_cols)
    leaderboard_13_df = convert_numeric(leaderboard_13_df, leaderboard_num_cols)

    # Add year_stage column
    leaderboard_15_df['year_stage'] = leaderboard_15_df['year'] + leaderboard_15_df['stage'] / 10
    leaderboard_14_df['year_stage'] = leaderboard_14_df['year'] + leaderboard_14_df['stage'] / 10
    leaderboard_13_df['year_stage'] = leaderboard_13_df['year'] + leaderboard_13_df['stage'] / 10

    # Create Pivot Tables for each year
    # ** 2015 **
    lb15_pivot = pd.pivot_table(leaderboard_15_df, values='score', index=['athlete_id', 'division'],
                                columns=['year_stage'], aggfunc='mean')
    lb15_pivot.reset_index(inplace=True)
    lb15_scaled_pivot = pd.pivot_table(leaderboard_15_df, values='scaled', index=['athlete_id', 'division'],
                                       columns=['year_stage'], aggfunc='mean')
    lb15_scaled_pivot.reset_index(inplace=True)
    lb15_scaled_pivot.columns = ['athlete_id', 'division', '15.1_scaled', '15.11_scaled', '15.2_scaled', '15.3_scaled',
                                 '15.4_scaled', '15.5_scaled']
    lb15_pivot = pd.merge(lb15_pivot, lb15_scaled_pivot, on=['athlete_id', 'division'], how='left')

    # ** 2014 **
    lb14_pivot = pd.pivot_table(leaderboard_14_df, values='score', index=['athlete_id', 'division'],
                                columns=['year_stage'], aggfunc='mean')
    lb14_pivot.reset_index(inplace=True)
    lb14_pivot['14.1_scaled'] = 0
    lb14_pivot['14.2_scaled'] = 0
    lb14_pivot['14.3_scaled'] = 0
    lb14_pivot['14.4_scaled'] = 0
    lb14_pivot['14.5_scaled'] = 0

    # ** 2013 **
    lb13_pivot = pd.pivot_table(leaderboard_13_df, values='score', index=['athlete_id', 'division'],
                                columns=['year_stage'], aggfunc='mean')
    lb13_pivot.reset_index(inplace=True)
    lb13_pivot['13.1_scaled'] = 0
    lb13_pivot['13.2_scaled'] = 0
    lb13_pivot['13.3_scaled'] = 0
    lb13_pivot['13.4_scaled'] = 0
    lb13_pivot['13.5_scaled'] = 0

    # Merge tables
    leaderboard_df = pd.merge(lb14_pivot, lb15_pivot, on=['athlete_id', 'division'], how='outer')
    leaderboard_df = pd.merge(leaderboard_df, lb13_pivot, on=['athlete_id', 'division'], how='outer')
    leaderboard_df = pd.merge(leaderboard_df, lb16_pivot, on=['athlete_id', 'division'], how='outer')
    leaderboard_df.set_index('athlete_id', inplace=True)

    # Remove bogus columns
    del (leaderboard_df[14.0])
    del (leaderboard_df[13.0])
    del (leaderboard_df[16.6])
    del (leaderboard_df['16.6_scaled'])

    # Close database connection
    conn.close()

    return leaderboard_df


def create_table_leaderboard_old(leaderboard_df, table_name='leaderboard_old'):
    conn = sqlite3.connect('open_2017.db')
    c = conn.cursor()

    pd_sql.to_sql(leaderboard_df, name=table_name, con=conn)
    # leaderboard_df.to_sql('leaderboard_old', conn, flavor='SQLite', if_exists='append', index=False)
    conn.close()


leaderboard_df = create_leaderboard_old()
print(leaderboard_df.columns)
print(leaderboard_df.reset_index().head())
print(leaderboard_df.reset_index().index)
create_table_leaderboard_old(leaderboard_df, table_name='leaderboard_new')
