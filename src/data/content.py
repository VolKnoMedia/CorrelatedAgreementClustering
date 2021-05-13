from src.data.meta import Meta
import collections
import bisect
import json
import ast
import numpy as np


class Content(Meta):
  def __init__(self, id, connector):
    super().__init__(id, connector)
    raw = self.run(f"""SELECT media_id, title, date_added , release_date
                    FROM media 
                    WHERE media_id = {self.id};
                    """)[0]

    self.title = raw[1]
    self.date_added = raw[2]
    self.release_date = raw[3]
  
  def getResults(self, resultType = 'EMOJI'):
    res = self.run(f"""SELECT user_id, media_time_secs, challenge_key 
                    FROM results 
                    WHERE code='{resultType}' AND media_item_id = {self.id};""")

    data = []
    for i in res:
        data.append(np.array([i[0], self.getSceneIdx(i[1]), i[2]]))
    self.results = np.asarray(data)
    return self.results


  def getScenes(self):
    scenes = ast.literal_eval(self.run(f"""SELECT scenes FROM media_items_meta WHERE media_id = {self.id} ;""")[0][0])
    temp = collections.OrderedDict()
    for idx, i in enumerate(scenes):
      temp[i['end']] = idx 
    self.scenes = temp
    return temp

  def getSceneIdx(self, timestamp):
    return bisect.bisect_left(list(self.scenes.keys()), timestamp)


