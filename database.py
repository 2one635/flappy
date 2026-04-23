import os
import sqlite3
import hashlib
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "flappybird.db")

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
    cursor.execute('''SELECT Player.Username, Score.Score, Score.TimeSurvived, Score.DateAchieved
               FROM Score
               JOIN Player ON Score.PlayerID = Player.PlayerID
               WHERE Score.GameMode = "endless"
               ORDER BY Score.Score DESC
               LIMIT 5''')
    endless_scores = cursor.fetchall()
    conn.close()
    return endless_scores

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

    # Check for Completionist achievement (Achievement 10)
    cursor.execute("SELECT COUNT(*) FROM PlayerAchievement WHERE PlayerID = ?", (player_id,))
    count = cursor.fetchone()[0]
    if count >= 9:  # all except completionist itself
        cursor.execute("SELECT * FROM PlayerAchievement WHERE PlayerID = ? AND AchievementID = 10", (player_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO PlayerAchievement (PlayerID, AchievementID, DateUnlocked) VALUES (?, ?, ?)",
                           (player_id, 10, date))
            conn.commit()

    conn.close()

def get_player_achievements(player_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Achievement.AchievementID, Achievement.Name, Achievement.Description,
               PlayerAchievement.DateUnlocked
        FROM PlayerAchievement
        JOIN Achievement ON PlayerAchievement.AchievementID = Achievement.AchievementID
        WHERE PlayerAchievement.PlayerID = ?
        ORDER BY PlayerAchievement.DateUnlocked ASC
    ''', (player_id,))
    achievements = cursor.fetchall()
    conn.close()
    return achievements

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

    achievements = [
        (1, "First Flight", "Played first game", "Login for the first time"),
        (2, "Level 1 Complete", "Beat level 1", "Complete level 1"),
        (3, "Level 2 Complete", "Beat level 2", "Complete level 2"),
        (4, "Level 3 Complete", "Beat level 3", "Complete level 3"),
        (5, "Level 4 Complete", "Beat level 4", "Complete level 4"),
        (6, "Level 5 Complete", "Beat level 5", "Complete level 5"),
        (7, "Persistent", "Fail 10 times", "Fail 10 times"),
        (8, "Survivor", "Reach a score of 20 in endless", "Score 20+ in endless mode"),
        (9, "Power Up", "Pick up a power-up", "Collect a power-up"),
        (10, "Completionist", "Unlock all achievements", "Unlock all achievements"),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO Achievement (AchievementID, Name, Description, Condition)
        VALUES (?, ?, ?, ?)
    ''', achievements)

    conn.commit()
    conn.close()

create_tables()