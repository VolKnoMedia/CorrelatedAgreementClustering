from src.data.content import Content
from src.data.db import DB

import pandas as pd

class Titles(DB):
  def __init__(self, connector, category='movie'):
    super().__init__(connector['host'], connector['user'], connector['password'])
    self.connector = connector
    self.titles = self.getTitles(category)
    self.content = {}

  def getData(self):
    self.getResponses()
    for i in self.content:
      try:
        self.content[i].getScenes()
        self.content[i].getResults()
        print(i, end =" ") 
      except:
        print("error", i, end=' ')

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


  def getList(self):
    self.getData()
    all = []
    for i in self.content:
      try:
        _title = self.content[i]
        _titleMeta = [i, _title.date_added, _title.title ]
        for k in self.content[i].results:
          res_list = [*k, *_titleMeta]
          all.append(res_list)
      except:
        pass
    return all
  
  def getDataFrame(self, columns=['user','sceneIdx','emotion','dateAdded','title']):
    data = self.getList()
    return pd.DataFrame(data, columns=columns)

  


  