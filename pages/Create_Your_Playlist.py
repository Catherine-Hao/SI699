import streamlit as st
import pandas as pd
import datetime as dt
import plotly.graph_objs as go
import plotly.figure_factory as ff
import altair as alt
import plotly.express as px
import os
import time
import random
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy


# set tab title
st.set_page_config(page_title="Create your pop music playlist", page_icon="🎶")

# load data
abs_path = os.path.dirname(__file__)
# full_path = os.path.join('/'.join(abs_path.split('/')[:-1]), 'data/spotify_pop_music.csv')
@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df
# music_df = load_data(full_path)
# music_df.drop_duplicates(inplace=True)
# music_df["release_date"] = pd.to_datetime(music_df["release_date"])
# music_df["year"] = music_df["release_date"].dt.year

shuffled_path = os.path.join('/'.join(abs_path.split('/')[:-1]), 'data/shuffled_spotify_pop_music.csv')
shuffled_music_df = load_data(shuffled_path)
shuffled_music_df.drop_duplicates(inplace=True)
shuffled_music_df["release_date"] = pd.to_datetime(shuffled_music_df["release_date"])
shuffled_music_df["year"] = shuffled_music_df["release_date"].dt.year


# set header 
st.header('Create your own pop music playlist')
st.subheader('To get started, what are you up to?')

# ============== select user context ============== 
selected_context = st.radio(
    "",
    ('Energize', 'Relax', 'Focus', 'Commute'))

# PCA + Kmeans: find the clustering with the selected user context
music_features_df = shuffled_music_df[
    [
        "danceability",
        "energy",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
    ]
]
music_features_df.fillna(0, inplace=True)
music_features_np = music_features_df.to_numpy()
# noramlize data
scaler = StandardScaler()
music_features_np = scaler.fit_transform(music_features_np)
# extract pca
pca = PCA(6)
pca_data = pca.fit_transform(music_features_np)
# kmeans clustering: 4 clusters
kmeans_model = KMeans(n_clusters=4, random_state=42, init="k-means++")
kmeans_labels = kmeans_model.fit_predict(pca_data)
# !!! this part is messed up !!!
# match contexts with labels
# 0-focus 1-relax 2-energize 3-commute
context_dict = {'Focus': 0, 'Relax': 1, 'Energize': 2, 'Commute': 3}
selected_context_label = context_dict[selected_context]
selected_context_indexes = [i for i in range(len(kmeans_labels)) if kmeans_labels[i] == selected_context_label]
selected_context_df = shuffled_music_df[(shuffled_music_df.index.isin(selected_context_indexes)) & (shuffled_music_df['popularity'] >= 50)]


# ============== user preference for music features ============== 
st.subheader('Next step, add your personal taste...')
danceability = st.slider('danceability', 0.0, 1.0, 0.5)
energy = st.slider('energy', 0.0, 1.0, 0.5)
speechiness = st.slider('speechiness', 0.0, 1.0, 0.5)
acousticness = st.slider('acousticness', 0.0, 1.0, 0.5)
instrumentalness = st.slider('instrumentalness', 0.0, 1.0, 0.5)
liveness = st.slider('liveness', 0.0, 1.0, 0.5)
valence = st.slider('valence', 0.0, 1.0, 0.5)

# ============== user listening history ============== 
st.subheader('Lastly, check the songs you\'re into...')

# set session state for change button
if 'key' not in st.session_state:
    st.session_state.key = 20
else:
    st.session_state.key = st.session_state.key


# change the list if there's none that user is interested
if st.button('change'):
    st.session_state.key = st.session_state.key + 20
    key = st.session_state.key
    user_interface_df = selected_context_df[['artist_name', 'track_name', 'release_date']].iloc[key+20:key+40, :]

# display checklist
key = st.session_state.key
if_check_list = []
checklist_indexes_list = []
user_interface_df = selected_context_df[['artist_name', 'track_name', 'release_date']].iloc[key+20:key+40, :]
for index, row in user_interface_df.iterrows():
    music_string = row['artist_name'] + ' - ' + row['track_name'] # + '-' + str(row['release_date'])
    agree = st.checkbox(music_string)
    checklist_indexes_list.append(index)
    if_check_list.append(agree)

# st.write(checklist_indexes_list)

# ============== make recommendations ============== 
# st.subheader('Here\'s your customized pop music playlist:')
# add blank space
st.markdown('##')
st.markdown('##')
if st.button("Generate your Spotify pop music playlist"):
    selected_check_indexs_list = [checklist_indexes_list[i] for i in range(len(if_check_list)) if if_check_list[i] == True]
    selected_check_df = selected_context_df[selected_context_df.index.isin(selected_check_indexs_list)]

    # calculate the mean of music features - from checked boxes and slidebars
    user_selected_features_np = [np.array([danceability, energy, speechiness, acousticness, instrumentalness, liveness, valence]).reshape(-1, )]
    for i in selected_check_df.index:
        user_selected_features_np.append(music_features_np[i])
    user_selected_features_mean_np = np.mean(np.stack(user_selected_features_np), axis=0)

    # calculate cosine similarity
    cosine_simi_dict = {}
    for i in selected_context_df.index:
        cosine_simi_dict[i] = cosine_similarity(
            user_selected_features_mean_np.reshape(1, -1),
            music_features_np[i].reshape(1, -1),
        )[0][0]

    # keep top 10 most similar
    top_10_similar_list = sorted(
        cosine_simi_dict.items(), key=lambda x: x[1], reverse=True
    )[:10]
    recommend_index_list = []
    for i in top_10_similar_list:
        recommend_index_list.append(i[0])

    # generate a recommended playlist of 10 songs
    recommend_df = selected_context_df[selected_context_df.index.isin(recommend_index_list)]
    # use spotipy to get the album cover 
    cid = "b9ff596f8afd419ab00f96c0e3ff1aff"
    secret = "fcc60a813705409090478d22581c726e"
    client_credentials_manager = SpotifyClientCredentials(
        client_id=cid, client_secret=secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    def get_album_cover_url(spotipy_obj, track_id):
        track_info = spotipy_obj.track(track_id)
        album_cover_url = track_info['album']['images'][0]['url']
        return album_cover_url

    recommend_df['url'] = 'https://open.spotify.com/track/' + recommend_df['id']

    for i in recommend_df.index:
        img_url = get_album_cover_url(sp, recommend_df.loc[i, 'id'])
        # # Option 1:
        st.image(img_url, width=300)
        st.caption(f"[{recommend_df.loc[i, 'track_name']}]({recommend_df.loc[i, 'url']})")
        # # Option 2:
        # st.markdown(f"[![Foo]({img_url})]({recommend_df.loc[i, 'url']})")
# st.dataframe(recommend_df[['artist_name', 'track_name', 'url']])




