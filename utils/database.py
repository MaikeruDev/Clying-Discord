import mysql.connector

# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="Clying"
)

def set_game(guild_id, channel_id):
    cursor = mydb.cursor()
     
    cursor.execute("SELECT guild_id FROM game_channels WHERE guild_id = %s", (guild_id,))
    result = cursor.fetchone()
    
    if result: 
        cursor.execute("UPDATE game_channels SET channel_id = %s WHERE guild_id = %s", (channel_id, guild_id))
    else: 
        cursor.execute("INSERT INTO game_channels (guild_id, channel_id) VALUES (%s, %s)", (guild_id, channel_id))
     
    mydb.commit()

def get_game_channel(guild_id):
    cursor = mydb.cursor()
    
    cursor.execute("SELECT channel_id FROM game_channels WHERE guild_id = %s", (guild_id,))
    result = cursor.fetchone()

    return result[0] if result else None