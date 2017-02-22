import sqlite3

conn = sqlite3.connect('open_2017.db')
c = conn.cursor()

# Create main leaderboard table
# try:
#     c.execute('''CREATE TABLE leaderboard
#                  (athlete_name text, athlete_id integer PRIMARY KEY, athlete_link text, pic text, region_name text, region_id integer, division integer,
#                  affiliate text, affiliate_id integer, occupation integer, scaled integer, age integer, height text, weight text, POS text, year integer,
#                  total_points text, score1 text, score2 text, score3 text, score4 text, score5 text, score6 text,
#                  rank1 text, rank2 text, rank3 text, rank4 text, rank5 text, rank6 text,
#                  score_id1 text, score_id2 text, score_id3 text, score_id4 text, score_id5 text, score_id6 text)''')
# except sqlite3.Error as e:
#     print "An error occurred (SQLite): ", e.args[0]

# Create athlete table
# try:
#     c.execute('''CREATE TABLE athletes
#                  (athlete_id integer PRIMARY KEY, athlete_name text, athlete_link text, pic text,
#                  region_name text, region_id integer, division integer, division_name text,
#                  affiliate text, affiliate_id integer, affiliate_link text, team text, team_id integer, team_link text,
#                  occupation integer, age integer, height text, height_cm integer, height_in integer,
#                  weight text, weight_lb integer, weight_kg integer,
#                  back_squat_lb integer, clean_and_jerk_lb integer, snatch_lb integer, deadlift_lb integer,
#                  fight_gone_bad integer, pull_ups integer, fran integer, grace integer, helen integer, filthy_50 integer,
#                  sprint_400m integer, run_5k integer
#                  )''')
# except sqlite3.Error as e:
#     print "An error occurred (SQLite): ", e.args[0]
#
# conn.commit()
