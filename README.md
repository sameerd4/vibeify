# Vibeify

https://www.vibeify.me

Vibeify is a tool that lets you make playlists for you and your friends. You can create party playlists with ease -- you just create a party, share the party ID like you would with Kahoot, and get your friends to join. Then, you start the party and get a mix of songs with something for everyone to love. If you're by yourself, you can use Vibeify to create mixes based on your mood. Sometimes you just need music for the moment.

Vibeify also tells you what your music says about you. Using Spotify's API, this app analyzes your favorite songs and provides information about what your favorite songs and artists are, and what kind of moods they represent. The app provides easily shareable and accessible images for social media.

The backend is in `app.py`, which holds the application logic for the Flask server, and `spotify_actions.py`, which uses the spotipy library for Spotify's API. `party_actions.py` provides more interactions with Spotify's API and handles party playlist creation. The frontend is in `static` and `templates`. It's the usual HTML/CSS/JS stack. Nothing fancy.

You might get an error if you don't have enough listening history. I'm working on fixing that.
