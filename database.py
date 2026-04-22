import os

DB_PATH = os.path.join(os.path.dirname(__file__), "flappybird.db")

import sqlite3
import hashlib
import datetime

def register_player(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
   
    hashed = hashlib.md5(password.encode()).hexdigest()
    
  
    cursor.execute("SELECT * FROM Player WHERE Username = ?", (username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return False  
    
   
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    
    cursor.execute("INSERT INTO Player (Username, PasswordHash, DateRegistered) VALUES (?, ?, ?)",
                   (username, hashed, date))
    
    conn.commit()
    conn.close()
    return True  

def login_player(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
  
    hashed = hashlib.md5(password.encode()).hexdigest()
    

    cursor.execute("SELECT * FROM Player WHERE Username = ? AND PasswordHash = ?", 
                   (username, hashed))
    player = cursor.fetchone()
    
    conn.close()
    
    if player:
        return player  
    else:
        return None  

def save_score(player_id, level_id, gamemode, score=None, time_survived=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    
    cursor.execute("INSERT INTO Score (PlayerID, LevelID, GameMode, Score, TimeSurvived, DateAchieved) VALUES (?, ?, ?, ?, ?, ?)",
                   (player_id, level_id, gamemode, score, time_survived, date))
    
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get top 10 scores with player usernames
    cursor.execute('''SELECT Player.Username, Score.GameMode, Score.TimeSurvived, Score.DateAchieved 
                   FROM Score 
                   JOIN Player ON Score.PlayerID = Player.PlayerID 
                   ORDER BY Score.TimeSurvived DESC 
                   LIMIT 10''')
    
    leaderboard = cursor.fetchall()
    conn.close()    
    return leaderboard

def save_achievement(player_id, achievement_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    
 
    cursor.execute("SELECT * FROM PlayerAchievement WHERE PlayerID = ? AND AchievementID = ?",
                   (player_id, achievement_id))
    existing = cursor.fetchone()
    
    if not existing:
        cursor.execute("INSERT INTO PlayerAchievement (PlayerID, AchievementID, DateUnlocked) VALUES (?, ?, ?)",
                       (player_id, achievement_id, date))
        conn.commit()
    
    conn.close()

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Player (
        PlayerID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT NOT NULL,
        PasswordHash TEXT NOT NULL,
        DateRegistered TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Score (
        ScoreID INTEGER PRIMARY KEY AUTOINCREMENT,
        PlayerID INTEGER NOT NULL,
        LevelID INTEGER,
        GameMode TEXT NOT NULL,
        Score INTEGER,
        TimeSurvived INTEGER,
        DateAchieved TEXT NOT NULL,
        FOREIGN KEY (PlayerID) REFERENCES Player(PlayerID),
        FOREIGN KEY (LevelID) REFERENCES Level(LevelID)
)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Level (
        LevelID INTEGER PRIMARY KEY AUTOINCREMENT,
        LevelNumber INTEGER NOT NULL,
        PipeSpeed INTEGER NOT NULL,
        GapSize INTEGER NOT NULL,
        PipeFrequency INTEGER NOT NULL,
        TimeLimit INTEGER NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Achievement (
        AchievementID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT NOT NULL,
        Condition TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS PlayerAchievement (
        PlayerAchievementID INTEGER PRIMARY KEY AUTOINCREMENT,
        PlayerID INTEGER NOT NULL,
        AchievementID INTEGER NOT NULL,
        DateUnlocked TEXT NOT NULL,
        FOREIGN KEY (PlayerID) REFERENCES Player(PlayerID),
        FOREIGN KEY (AchievementID) REFERENCES Achievement(AchievementID)
    )''')

    conn.commit()
    conn.close()

create_tables()