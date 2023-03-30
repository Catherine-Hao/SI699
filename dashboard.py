import streamlit as st
import pandas as pd
import datetime as dt
# import plotly.graph_objs as go
import plotly.figure_factory as ff
import altair as alt
import plotly.express as px
# import os

# load data
# abs_path = os.path.dirname(__file__)
# full_path = os.path.join(abs_path, 'spotify_pop_music.csv')
music_df = pd.read_csv(r'spotify_pop_music.csv')
music_df.drop_duplicates(inplace=True)
music_df["release_date"] = pd.to_datetime(music_df["release_date"])
music_df["year"] = music_df["release_date"].dt.year

# set tab title
st.set_page_config(page_title="Pop Music Analytics on Spotify dataset", page_icon="🎶")

# set header 
st.header('Pop Music Analytics on Spotify dataset')
st.subheader('Data View')

# data view
st.dataframe(music_df.sample(5))

# box plots - musical features evolve over time
music_features_columns = [
    "danceability",
    "energy",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
]

st.subheader('How the musical features evolve over time?')
box_option = st.selectbox(
    'Music features',
    tuple(music_features_columns),
    key='box_option')

music_features_box = px.box(
    music_df,
    x="year",
    y=box_option
)
st.plotly_chart(music_features_box, theme="streamlit", use_container_width=True)

# dist plots - styles of artists evolve over time
st.subheader('How the music styles of artists evolve over time?')
top_10_artists = music_df["artist_name"].value_counts().index[:10]

dist_option_artists = st.multiselect(
    'Top 10 Artists',
    top_10_artists,
    ['Taylor Swift'])

dist_option_features = st.selectbox(
    'Music features',
    tuple(music_features_columns),
    key='dist_option_features')

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
