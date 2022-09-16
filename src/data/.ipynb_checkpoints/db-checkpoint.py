import mysql.connector

class DB:
    def __init__(self, host, user, password):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database="heroku_app_db",
            charset='utf8',
            #use_unicode=True,
            #use_pure=True)
        )
    def run(self, sql):
        mycursor = self.db.cursor()
        self.db.set_unicode(True)
        mycursor.execute(sql)
        try:
            myresult = mycursor.fetchall()
        except:
            myresult = None
        self.db.commit()
        mycursor.close()
        return myresult
                
        

