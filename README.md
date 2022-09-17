# plex_db_date_added_fix
If viewing movies in Plex by "Date Added" orders the library all wrong, this could fix it.

I like to view my library by "Date Added" so that, as the library grows, I can see what is most recent.

I started using Plex with a decent sized library already so, when I created the Plex server, the "Date Added" for each movie were all over the place.

The solution I would've liked is to have it adopt the movie's folder's creation date, so I to made the option.

Plex now uses its own version of SQLite, so this will send an UPDATE command into Plex SQLite. It piped the command so that they can remain one-line commands and keep looping through my movies folder. For me, this ran on approx. 650 movies in 94 seconds.

## BEFORE YOU RUN THIS !

- Make a backup of your Plex database file just in case!
- I had problems running this script on Windows. Linux or OSX are much happier piping a command into another program I guess. Piping the command was the only way I could get it to pop these updates into the database as one-line commands.

### Recommended Instructions:
* Required: Python 3.x
0. Stop Plex (stop the docker or whatever)
1. Make two copies of the DB file (one to fix, one to remain as backup)
2. Run this script on ONE of the copies. While it runs, all I see is it repeating b'' a bunch of times.
3. Check that it worked by opening the DB file in 'DB Browser for SQLite' (https://sqlitebrowser.org/)
- Under 'Browse Data', select the table 'metadata_items'
- filter 'guid' with plex://movie and scroll way over to the right of the columns to find 'added_at' and click it to sort by that column
- [Unix time converter](https://time.is/Unix_time_converter) to check some of them. It should have fixed any titles with simple enough names (no special characters)
- Optional:
- If you want to fix any manually, titles like **Amélie** or **Léon: the Professional**, use the command template below and run a few manually.
4. Copy the fixed DB file into place in Plex's db folder
5. Start Plex again and confirm it works


## The database location:
- .../plex/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db

## The command template:

> echo 'UPDATE metadata_items SET added_at = 1193768357 WHERE title REGEXP "Kill Bill Vol 1" | "/Applications/Plex Media Server.app/Contents/MacOS/Plex SQLite" "/Users/chrisparsell/github/plexsql/database.db"

This script will make each folder name into a regular expression that looks for optional character (colons, commas, periods, question marks, and apostrophes)
By adding :?\??,?'?.? between each character of the folder name, the folder name "Kill Bill Vol 1" will match the database's title "Kill Bill: Vol. 1"

The final form of the full command looks something like this: 

> echo 'UPDATE metadata_items SET added_at = 1193768357 WHERE title REGEXP "K:?\??,?'?.?i:?\??,?'?.?l:?\??,?'?.?l:?\??,?'?.? :?\??,?'?.?B:?\??,?'?.?i:?\??,?'?.?l:?\??,?'?.?l:?\??,?'?.? :?\??,?'?.?V:?\??,?'?.?o:?\??,?'?.?l:?\??,?'?.? :?\??,?'?.?1:?\??,?'?.?"

Currently, it does not account for characters with accents like é
It also won't work for titles where the folder name is too different from the database's title

For example, the folder name "Raid Redemption" and the database's title "The Raid" won't be a match.
The folder name "Darjeeling Limited" won't match the database's title "The Darjeeling Limited" either
For myself, this still fixed the vast majority of my database.


