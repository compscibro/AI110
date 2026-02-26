# Playlist Chaos

Your AI assistant tried to build a smart playlist generator. The app runs, but some of the behavior is unpredictable. Your task is to explore the app, investigate the code, and use an AI assistant to debug and improve it.

This activity is your first chance to practice AI-assisted debugging on a codebase that is slightly messy, slightly mysterious, and intentionally imperfect.

You do not need to understand everything at once. Approach the app as a curious investigator, work with an AI assistant to explain what you find, and make targeted improvements.

---

## How the code is organized

### `app.py`  

The Streamlit user interface. It handles things like:

- Showing and updating the mood profile  
- Adding songs  
- Displaying playlists  
- Lucky pick  
- Stats and history

### `playlist_logic.py`  

The logic behind the app, including:

- Normalizing and classifying songs  
- Building playlists  
- Merging playlist data  
- Searching  
- Computing statistics  
- Lucky pick mechanics

You will need to look at both files to understand how the app behaves.

---

## What you will do

### 1. Explore the app  

Run the app and try things out:

- Add several songs with different titles, artists, genres, and energy levels  
- Change the mood profile  
- Use the search box  
- Try the lucky pick  
- Inspect the playlist tabs and stats  
- Look at the history  

As you explore, write down at least five things that feel confusing, inconsistent, or strange. These might be bugs, quirks, or unexpected design decisions.

### 2. Ask AI for help understanding the code  

Pick one issue from your list. Use an AI coding assistant to:

- Explain the relevant code sections  
- Walk through what the code is supposed to do  
- Suggest reasons the behavior might not match expectations  

For example:

> "Here is the function that classifies songs. The app is mislabeling some songs. Help me understand what the function is doing and where the logic might need adjustment."

Before making changes, summarize in your own words what you think is happening.

### 3. Fix at least four issues  

Make improvements based on your investigation.

For each fix:

- Identify the source of the issue  
- Decide whether to accept or adjust the AI assistant's suggestions  
- Update the code  
- Add a short comment describing the fix  

Your fixes may involve logic, calculations, search behavior, playlist grouping, lucky pick behavior, or anything else you discover.

### 4. Test your changes  

After each fix, try interacting with the app again:

- Add new songs  
- Change the profile  
- Try search and stats  
- Check whether playlists behave more consistently  

Confirm that the behavior matches your expectations.

### 5. Optional stretch goals  

If you finish early or want an extra challenge, try one of these:

- Improve search behavior  
- Add a "Recently added" view  
- Add sorting controls  
- Improve how Mixed songs are handled  
- Add new features to the history view  
- Introduce better error handling for empty playlists  
- Add a new playlist category of your own design  

---

## Tips for success

- You do not need to solve everything. Focus on exploring and learning.  
- When confused, ask an AI assistant to explain the code or summarize behavior.  
- Test the app often. Small experiments reveal useful clues.  
- Treat surprising behavior as something worth investigating.  
- Stay curious. The unpredictability is intentional and part of the experience.

When you finish, Playlist Chaos will feel more predictable, and you will have taken your first steps into AI-assisted debugging.
