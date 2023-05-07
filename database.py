import psycopg2

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="bkchatbot",
            user="server",
            password="123456789",
            port = 5432
        )
        self.cursor = self.conn.cursor()
    
    def insert_voice(self, voice_filename):
        sql = "INSERT INTO voice (voice_filename) VALUES (%s)"
        values = (voice_filename,)
        self.cursor.execute(sql, values)
        self.conn.commit()

    def insert_conversation(self, conversation_id):
        sql = "INSERT INTO conversation (conversation_id) VALUES (%s)"
        values = (conversation_id,)
        self.cursor.execute(sql, values)
        self.conn.commit()

    def insert_utterance(self, v_id, utterance_content, isInput, conv_id, time_st, pa_id):
        sql = "INSERT INTO utterance (v_id, utterance_content, isInput, conv_id, time_st, pa_id) VALUES (%s,%s,%s,%s,%s,%s)"
        values = (v_id, utterance_content, isInput, conv_id, time_st, pa_id)
        self.cursor.execute(sql, values)
        self.conn.commit()

    def get_voiceid(self):
        sql = "SELECT * FROM voice ORDER BY voice_id DESC"
        self.cursor.execute(sql)
        self.conn.commit()
        return self.cursor.fetchone()[0]
        
    
    def close_connection(self):
        self.cursor.close()
        self.conn.close()
