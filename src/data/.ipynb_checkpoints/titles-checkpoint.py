from src.data.content import Content
from src.data.db import DB

import pandas as pd

class Titles(DB):
  def __init__(self, connector, category='movie', topScenes='all'):
    super().__init__(connector['host'], connector['user'], connector['password'])
    self.connector = connector
    self.titles = self.getTitles(category)
    self.content = {}
    self.top = topScenes if topScenes != 'all' else False

  def getData(self):
    for i in self.content:
      try:
        self.content[i].getScenes()
        self.content[i].getResults(resultType='EMOJI', topScenes=self.top)
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
  
  def getDataFrame(self, columns=['user','sceneIdx','emotion','contentIdx','dateAdded','title']):
    data = self.getList()
    return pd.DataFrame(data, columns=columns)


  def getAllRatings(self):
    self.getResponses()
    allData = []
    for title in self.titles:
      try:
        data = self.content[title].getRatings()
        genre = self.content[title].getGenre()
        _titleMEta = [title, genre]
        for ratings in data:
          new = [*_titleMEta, *ratings]
          allData.append(new)
      except: 
        print("error", title, end=' ')
    return allData

  