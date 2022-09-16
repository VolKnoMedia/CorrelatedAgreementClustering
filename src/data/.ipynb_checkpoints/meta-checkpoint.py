from src.data.db import DB
import json


class Meta(DB):
  def __init__(self, id, connector):
    super().__init__(connector['host'], connector['user'],connector['password'])
    self.id = id

  def getGenre(self ):
    genres = self.run(f"""SELECT g.name
          FROM media_genres m 
          INNER JOIN genres g ON g.genre_id = m.genre_id
          WHERE media_id = {self.id}""")
    g = [i[0] for i in genres]
    return g

  def getRatings(self):
    res = self.run(f"""SELECT user_id, challenge_value, challenge_key, date_added
                      FROM results
                      WHERE media_id = {self.id} AND code = 'SUMMARY'; """)
    results = []
    for i in res:
      u = i[0]
      res = json.loads(i[1])
      resType = i[2]
      date = i[3]
      if resType == 'overall-rating':
        results.append((u, res['rating'], date))
    return results
  
  def getPerformance(self):
    return self.run(f"""SELECT media_id, imdb_budget, imdb_gross_usa, imdb_gross_worldwide, rottentomatoes_tomatometer, rottentomatoes_audience_score 
           FROM media_meta
           WHERE media_id = {self.id}""")