import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from altair import Row, Column, Chart, Text, Scale, Color, X, Y, Bin, SortField, LayeredChart


def create_score_hist(s, num_steps=30, step=None):
    hist_df = hist_series(s, num_steps=num_steps, step=step)

    hist_chart = Chart(hist_df).mark_bar().encode(
        x=X('Score Range:N',
            scale=Scale(bandSize=50.0),
            sort=SortField(field='Score Range', order='descending'),
            ),
        y=Y('Number of Scores:Q')
    )
    return hist_chart, hist_df


def create_score_hist_colored(s, num_steps=30, step=None, athlete_score=None):
    hist_df = hist_series(s, num_steps=num_steps, step=step, athlete_score=athlete_score)

    hist_chart = Chart(hist_df).mark_bar().encode(
        x=X('Score Range:N',
            scale=Scale(bandSize=50.0),
            sort=SortField(field='Score Range', order='descending'),
            ),
        y=Y('Number of Scores:Q'),
        color=Color('Score Type:N',
                    scale=Scale(
                        range='category10')
                    )
    )

    return hist_chart, hist_df


def hist_series(s, step=None, min_range=0, max_range=None, num_steps=20, athlete_score=None):
    if max_range is None:
        max_range = max(np.nanmax(s)) + 1

    if (step is None) and (type(num_steps) is int):
        step = np.ceil(max_range / num_steps / 10) * 10

    bin_range = np.arange(min_range, max_range + step, step)
    label_range = np.arange(min_range - step / 2, max_range + step / 2, step)
    out, bins = pd.cut(s, bins=bin_range, include_lowest=True, right=False, retbins=True,
                       labels=label_range[1:])
    hist_s = out.value_counts(sort=False)

    hist_df = pd.DataFrame(hist_s)
    hist_df.reset_index(inplace=True)
    hist_df.columns = ['Score Range', 'Number of Scores']
    hist_df.sort_values('Score Range', ascending=True, inplace=True)
    hist_df.reset_index(inplace=True)
    del (hist_df['index'])
    hist_df['Score Range'] = hist_df['Score Range'].apply(int)

    hist_df['Score Type'] = 'Community'
    if not athlete_score is None:
        athlete_bin = np.digitize([athlete_score], bins)[0]-1
        hist_df.loc[athlete_bin, 'Score Type'] = "Athlete"

    return hist_df
