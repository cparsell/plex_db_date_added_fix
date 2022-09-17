import subprocess
import os
import pipes

# ! BEFORE YOU RUN THIS !
# 
# Make a backup of your Plex database file just in case!
# 
# What I do:
#   0. Stop Plex (stop the docker or whatever)
#   1. Make two copies of the DB file (one to fix, one to remain as backup)
#   2. Run this script on ONE of the copies. While it runs, all I see is it repeating b'' a bunch of times.
#   3. Check that it worked by opening the DB file in 'DB Browser for SQLite' (https://sqlitebrowser.org/)
#     3a. Under 'Browse Data', select the table 'metadata_items'
#     3b. filter 'guid' with plex://movie and scroll way over to the right of the columns to find 'added_at' and click it to sort by that column
#     3c. https://time.is/Unix_time_converter to check some of them. It should have fixed any titles with simple enough names (no special characters)
#   3. Copy the fixed DB file into place in Plex's db folder
#   4. Start Plex again and confirm it works
#
# The database location:
# .../plex/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db
# 
# The command this runs to fix this:
# 
#   echo 'UPDATE metadata_items SET added_at = 1193768357 WHERE title REGEXP "Kill Bill Vol 1" | "/Applications/Plex Media Server.app/Contents/MacOS/Plex SQLite" "/Users/johndoe/github/plexsql/database.db"
# 
# This script will make each folder name into a regular expression that looks for optional character (colons, commas, periods, question marks, and apostrophes)
# By adding :?\??,?'?.? between each character of the folder name, the folder name "Kill Bill Vol 1" will match the database's title "Kill Bill: Vol. 1"
# 
# The final form of the full command looks something like this: 
# 
#   echo 'UPDATE metadata_items SET added_at = 1193768357 WHERE title REGEXP "K:?\??,?'?.?i:?\??,?'?.?l:?\??,?'?.?l:?\??,?'?.? :?\??,?'?.?B:?\??,?'?.?i:?\??,?'?.?l:?\??,?'?.?l:?\??,?'?.? :?\??,?'?.?V:?\??,?'?.?o:?\??,?'?.?l:?\??,?'?.? :?\??,?'?.?1:?\??,?'?.?"
# 
# Currently, it does not account for characters with accents like é
# It also won't work for titles where the folder name is too different from the database's title
# 
# For example, the folder name "Raid Redemption" and the database's title "The Raid" won't be a match.
# The folder name "Darjeeling Limited" won't match the database's title "The Darjeeling Limited" either
# For myself, this still fixed the vast majority of my database.

# I had problems running this script on Windows. Linux or OSX are much happier piping a command into another program I guess.

# Make sure these locations match yours:

# Movies Folder:
movies_dir = "/Users/johndoe/movies/"

# Location of Plex SQLite
# sql = "C:\\Program Files (x86)\\Plex\\Plex Media Server\\Plex SQLite.exe"
sql = "/Applications/Plex Media Server.app/Contents/MacOS/Plex SQLite"

# Copy of the DB file to operate on:
# db = "/Users/johndoe/Desktop/Plex db/com.plexapp.plugins.library.db"
db = "/Users/johndoe/github/plexsql/database.db"

def regexTitle (title):
  newstring = ""
  # Loop through title and add :?\??,?'?.? between each character, accounting for possible commas, colons, etc.
  for letter in enumerate(title):
    newstring = newstring + letter[1] + ":?\??,?'?.?"
  return newstring

for folder in os.listdir(movies_dir):
  # full path, directory and filename
  fullpath = os.path.join(movies_dir,folder)
  # get date folder was created
  ctime = os.path.getctime(fullpath)
  # get rid of year and () in folder name
  movie = folder.split(" (")[0]

  #Loop through each folder, excluding folders like .DS_Store or .Trash-1000
  if folder != ".DS_Store" and folder != ".Trash-1000":
    # Create regular expression out of the folder name
    movie_regex = regexTitle(movie)

    # arguments 
    sql_update = 'UPDATE metadata_items SET added_at = %s WHERE title REGEXP \"%s\"'%(int(ctime), str(movie_regex))

    # initial part of the command
    # echo 'UPDATE metadata_items SET added_at = 1193768357 WHERE title REGEXP "Kill Bill Vol 1"
    args = ['echo', sql_update]
    
    # alternate command - had more problems with apostrophes in folder names
    # os.system("echo \"%s\" | \"%s\" \"%s\""%(sql_update, sql_osx, db_osx))

    # create process for initial part
    ps = subprocess.Popen(args, stdout=subprocess.PIPE)
    # pipe it into Plex SQLite with the DB file location
    output = subprocess.check_output((sql, db), stdin=ps.stdout)
    ps.wait()
    print(output)  
    
print ("Operation complete.")
