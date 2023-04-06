import streamlit as st
import pandas as pd
import datetime as dt
import plotly.graph_objs as go
import plotly.figure_factory as ff
import altair as alt
import plotly.express as px
import os
import time

# set tab title
st.set_page_config(page_title="Pop Music Analytics on Spotify dataset", page_icon="🎶")


# load data
abs_path = os.path.dirname(__file__)
full_path = os.path.join(abs_path, 'spotify_pop_music.csv')

@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df
music_df = load_data(full_path)
# music_df = pd.read_csv(full_path)
music_df.drop_duplicates(inplace=True)


# set header 
st.header('Pop Music Analytics on Spotify dataset')
st.subheader('Data View')

# data view
sample_music_df = music_df.sample(5).copy()
sample_music_df.reset_index(inplace=True)
music_features_columns = [
    "danceability",
    "energy",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
]
display_columns = ['artist_name', 'track_name', 'popularity', 'release_date'] + music_features_columns +['key', 'loudness', 'mode', 'tempo', 'duration_ms']
st.dataframe(sample_music_df[display_columns])

# box plots - musical features evolve over time
music_df["release_date"] = pd.to_datetime(music_df["release_date"])
music_df["year"] = music_df["release_date"].dt.year
top_10_artists = music_df["artist_name"].value_counts().index[:10]

st.subheader('How are the musical features evolving over time?')
box_option = st.selectbox(
    'Music features',
    tuple(music_features_columns),
    key='box_option')

box_option_artists = st.multiselect(
    'Select an artist',
    top_10_artists, 
    [])

# # Choice 1: box plot
# if not box_option_artists:
#     music_features_box = px.box(
#         music_df,
#         x="year",
#         y=box_option
#     )
# else:
#     music_features_box = px.box(
#         music_df[music_df["artist_name"].isin(box_option_artists)],
#         x="year",
#         y=box_option
#     )
# st.plotly_chart(music_features_box, theme="streamlit", use_container_width=True)

# Choice 2: line plot
if not box_option_artists:
    selected_artist_tracks_df = music_df
else:
    selected_artist_tracks_df = music_df[music_df['artist_name'].isin(box_option_artists)]

y_mean = selected_artist_tracks_df.groupby('year').mean()[box_option].to_list()
y_std = selected_artist_tracks_df.groupby('year').std()[box_option].to_list()
# y_max = selected_artist_tracks_df.groupby('year').max()[box_option].to_list()
# y_min = selected_artist_tracks_df.groupby('year').min()[box_option].to_list()
y_max = [y_mean[i]+1*y_std[i] for i in range(len(y_mean))]
y_min = [y_mean[i]-1*y_std[i] for i in range(len(y_mean))]
x = selected_artist_tracks_df.groupby('year').mean().index.to_list()

fig = go.Figure([
    go.Scatter(
        x=x,
        y=y_mean,
        line=dict(color='rgb(0,100,80)'),
        mode='lines',
        name="mean"
    ),
    go.Scatter(
        x=x+x[::-1], # x, then x reversed
        y=y_max+y_min[::-1], # upper, then lower reversed
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name="mean ± std"
    )
])


fig.update_layout(xaxis_range=[min(x),max(x)], 
                  yaxis_range=[0,1], 
                  xaxis_title="year", 
                  yaxis_title=box_option)

st.plotly_chart(fig, use_container_width=True)

# dist plots - styles of artists evolve over time
st.subheader('How are the music styles of most popular artists distributed?')

dist_option_features = st.selectbox(
    'Music features',
    tuple(music_features_columns),
    key='dist_option_features')

dist_option_artists = st.multiselect(
    'Select an artist',
    top_10_artists,
    ['Taylor Swift'])

group_labels = dist_option_artists

selected_music_df_list = []
for i in dist_option_artists:
    selected_music_df_list.append(music_df[music_df['artist_name'] == i][dist_option_features])

artists_dist = ff.create_distplot(selected_music_df_list, group_labels)
st.plotly_chart(artists_dist, theme="streamlit", use_container_width=True)


# heatmap - relationship between popularity and musical features 
st.subheader('How is popularity related to musical features?')
popularity_df = music_df[
    [
        "popularity",
        "danceability",
        "energy",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
    ]
]
popularity_corr = popularity_df.corr()
popularity_heatmap = px.imshow(popularity_corr, color_continuous_scale='RdBu_r',)
st.plotly_chart(popularity_heatmap, theme="streamlit",  use_container_width=True)




