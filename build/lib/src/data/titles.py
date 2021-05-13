from src.data.content import Content
from src.data.db import DB

class Titles(DB):
  def __init__(self, connector, category='movie'):
    super().__init__(connector['host'], connector['user'], connector['password'])
    self.connector = connector
    self.titles = self.getTitles(category)
    self.content = {}


  def getResponses(self, debug = False):
    for titleId in self.titles:
      try:
        self.content[titleId] = Content(titleId, self.connector)
      except:
        print("Error", titleId)



  def getTitles(self, category):
    typeid = 1 if category == 'movie' else 2 if category == 'tv' else 3
    resp = self.run(f"""SELECT media_id
           FROM media 
           WHERE media_type_id = {typeid};""")
    return [i[0] for i in resp]