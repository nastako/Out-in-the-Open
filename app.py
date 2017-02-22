import os, sys
import datetime as dt
import pandas as pd
import numpy as np
import json
from scipy import stats as scipy_stats
from flask import Flask, jsonify, request, Response
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator, RawTag
from flask_bootstrap import Bootstrap

pd.set_option("display.max_columns", None)

from forms import InsightForm, RecordForm
from nav import nav

from library.data_connect import *
from library.plot_tools import *

# Start Flask app
print('Starting Flask app')
app = Flask(__name__)

# Install our Bootstrap extension
Bootstrap(app)

# TODO CHANGE!
SECRET_KEY = 'devkey'
app.secret_key = SECRET_KEY

# Because we're security-conscious developers, we also hard-code disabling
# the CDN support (this might become a default in later versions):
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top', Navbar(
    View('Out in the Open', '.index'),
    View('Main Dashboard', '.dashboard'),
    View('Personal Insights', '.insight'),
    # RawTag('http://www.w3schools.com/images/colorpicker.gif', type='img')
))

rawtag = RawTag('http://www.w3schools.com/images/colorpicker.gif', type='img')
# print(rawtag.content)
# print(rawtag.attribs)
# print(rawtag.render())

# We initialize the navigation as well
nav.init_app(app)

# Year to stages dict
# TODO: Fix 2016+
year_stages = {2013: [13.1, 13.2, 13.3, 13.4, 13.5],
               2014: [14.1, 14.2, 14.3, 14.4, 14.5],
               2015: [15.1, 15.11, 15.2, 15.3, 15.4, 15.5],
               2016: [16.1, 16.2, 16.3, 16.4, 16.5],
               2017: [16.1, 16.2, 16.3, 16.4, 16.5]}
all_stages = [16.5, 16.4, 16.3, 16.2, 16.1, 15.5, 15.4, 15.3, 15.2, 15.1, 15.11, 14.5, 14.4, 14.3, 14.2, 14.1]
i_stages = [4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0, 4, 3, 2, 1, 0, 4, 3, 2, 1, 0]

# Year to step size dict
step_size_dict = {2013: [10, 10, 4, 8, 120],
                  2014: [10, 10, 4, 8, 120],
                  2015: [10, 10, 10, 30, 16, 80],
                  2016: [10, 10, 4, 8, 120],
                  2017: [10, 10, 4, 8, 120],
                  }

# Year to rank order
rank_order_dict = {2013: [False, False, False, False, True],
                   2014: [False, False, False, False, True],
                   2015: [False, False, False, False, False, True],
                   2016: [False, False, False, False, True],
                   2017: [False, False, False, False, True],
                   }


def start_app():
    """
    Initialize Flask application.
    Sets the IP as 0.0.0.0 (may need to be 'localhost' on Windows) at port 5002 (http://0.0.0.0:5010)
    Debug setting is on
    Multi-threading is on
    Reloading is set on (when code is altered while app is running, app will restart)
    """
    app.run(host="0.0.0.0", debug=True, port=5010, processes=True, use_reloader=True)


@app.route('/', methods=['GET'])
def test():
    """
    For testing API at http://0.0.0.0:5010/
    :return: Simple json message
    """
    return jsonify({'message': 'Welcome to Open Analyzer'})


@app.route('/index', methods=['GET'])
def index():
    form = InsightForm()
    print('Success')
    return render_template('index.html', form=form)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    division = 1

    year = 2014
    stages = year_stages[year]
    step_size = step_size_dict[year]

    results_df = get_results_old(division=division, stages=stages)

    json_charts = []
    for i, stage in enumerate(stages):
        hist_chart, hist_df = create_score_hist(results_df[str(stage)], step=step_size[i])
        hist_chart.width = 600
        hist_chart.height = 150

        hist_chart_json = hist_chart.to_json()
        hist_chart_json = json.loads(hist_chart_json)
        json_charts.append(hist_chart_json)

    years = [int(np.floor(r)) for r in stages]
    stage_num = [int(str(r).split('.')[-1]) for r in stages]

    # print(hist_chart_json)
    return render_template('dashboard2.html', all_charts=json_charts,
                           stages=stage_num, years=years)


@app.route('/insight', methods=['GET', 'POST'])
def insight():
    form = InsightForm()

    json_charts = []
    years = []
    stages = []
    vals = []
    athlete_stats = []
    if form.validate_on_submit():
        athlete_id = form.athlete_id.data

        athlete_df = get_old_athlete(athlete_id)
        gender_num = athlete_df['gender_num'].loc[0]
        if gender_num == 0:
            division = 2
        else:
            division = gender_num

        # print(athlete_df)

        # stages = year_stages[year]
        stages = all_stages

        results_df = get_results_new(division=division, stages=stages)
        # print(results_df.head())

        athlete_stats = results_df[results_df['athlete_id'] == athlete_id].to_dict('records')[0]
        # print(athlete_stats)

        years = [int(np.floor(r)) for r in stages]
        stage_num = [int(str(r).split('.')[-1]) for r in stages]

        for i, stage in enumerate(stages):
            i_stage = i_stages[i]
            stage_scaled = str(stage) + '_scaled'

            year = 2000 + int(np.floor(stage))
            step_size = step_size_dict[year]

            filtered_results_df = results_df.copy()
            fltr_scaled = filtered_results_df[stage_scaled] == athlete_stats[stage_scaled]
            filtered_results_df = filtered_results_df[fltr_scaled]

            fltr_athlete = filtered_results_df['athlete_id'] == athlete_id

            stage_results = filtered_results_df[str(stage)]
            athlete_score = filtered_results_df.loc[fltr_athlete, str(stage)].iloc[0]
            max_score = max(np.nanmax(stage_results))
            mean_score = np.nanmean(np.array(stage_results))
            median_score = np.nanmedian(np.array(stage_results))

            rank_order = rank_order_dict[year][i_stage]
            stage_ranks = stage_results.rank(method='first', ascending=rank_order)
            athlete_rank = stage_ranks[fltr_athlete].iloc[0]

            num_stage_scores = stage_results.count()
            athlete_percentile = np.floor((num_stage_scores - athlete_rank) * 1000 / (num_stage_scores - 1)) / 10

            hist_chart, hist_df = create_score_hist_colored(stage_results, step=step_size[i_stage],
                                                            athlete_score=athlete_score)
            hist_chart.width = 700
            hist_chart.height = 300

            hist_chart_json = hist_chart.to_json()
            hist_chart_json = json.loads(hist_chart_json)
            json_charts.append(hist_chart_json)

            stats = dict(athlete_score=int(athlete_score), max_score=int(max_score), mean_score=int(mean_score),
                         median_score=int(median_score), athlete_rank=int(athlete_rank),
                         athlete_percentile=athlete_percentile)

            val_dict = dict(chart=hist_chart_json, stage=stage_num[i], year=years[i], stats=stats)
            vals.append(val_dict)

    return render_template('insight.html', form=form, vals=vals, athlete=athlete_stats)


if __name__ == '__main__':
    # If script is run from command like (like: python waiter/api.py), start application
    start_app()
