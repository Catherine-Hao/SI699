# 🎶 SI699

This project creates a pop music analytics dashboard and a multi-context-aware music recommender system with Spotify API. 

Contact haorlin@umich.edu.


Data access statement
---------------
The data from this project is accessed via [Spotify Web API] (https://developer.spotify.com/documentation/web-api), which enables the creation of applications that can interact with Spotify's streaming service, such as retrieving content metadata, getting recommendations, creating and managing playlists, or controlling playback. Users gain access to the credentials when creating an application. These will be required for API authorization to obtain an access token, and access token are required in API requests.


How to run the app?
---------------
First get the source code of this project. Do this by cloning the whole repository:

```bash
# Clone the example project repo
git clone https://github.com/Catherine-Hao/SI699.git
```

Then install some dependencies:

```bash
pip install -r SI699/requirements.txt
```

Finally the following command will setup the streamlit application, and start the server:

```bash
streamlit run /SI699/code/Music_Analytics.py
```

Now we can view this application in the browser with a local or network URL [(example)](https://catherine-hao-si699-music-analytics-xw280c.streamlit.app/).


