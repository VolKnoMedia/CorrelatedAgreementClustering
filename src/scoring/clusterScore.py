from src.utils import CorrelationStructure
import numpy as np
import pandas as pd

class Scores:
  def __init__(self, kmean, method='standard'):
    self.clusters = kmean.clusters
    self.globalScene = kmean.globalScene
    self.users = kmean.users
    self.K = kmean.K
    self.scores =  [ScoreStruct(k.struct) for k in self.clusters]

    for i in self.scores:
      i.getScores(method=method)

  def score(self, method='standard', n=20, debug=True):
    scores = {}
    for uid in self.users:
      if method == 'standard':
        user = self.users[uid]
        userScore = self.standardUserScore(user, n=n)
        user.score = userScore
        scores[uid]= userScore
        if debug:
          print(uid, userScore)
      elif method == 'binary':
        user = self.users[uid]
        userScore = self.standardUserScore(user, n=n, debug=False)
        user.score = userScore
        scores[uid]= userScore
        if debug:
          print(uid, userScore)

    self.userScores = scores

  def standardUserScore(self, _u, n=20, debug=False):
    scores = []
    for idx, sceneX in enumerate(_u.scenes):
      x = _u.emotions[idx]
      score = []
      if debug:
        print(sceneX, x, _u.getCluster())
      for _ in range(0, n):
        # get another user __u and response y from same scene
        __uId, y = self._getY(sceneX)
        
        __u = self.users[__uId]

        # another response by user u. x'
        sceneX_, x_ = self._getX(_u)

        # get y''
        y_ = self._getYprime(__u, sceneX_, sceneX)
        
        c1 = _u.getCluster()
        c2 = __u.getCluster()
       

        s1 = self.scores[c1][c2][x, y]
        s2 = self.scores[c1][c2][x_, y_]

        if debug:
          print("\t",__uId, c2,'=', y, s1, " : ", x_, y_, s2)

        score.append(s1-s2)
      if debug:
        print('\t Avg: ', sum(score) / n)
      scores.append(sum(score) / n)
    return sum(scores)


  def uscore(self, _u, n=20, clust=0):
    scores = []
    for idx, sceneX in enumerate(_u.scenes):
      x = _u.emotions[idx]
      score = []
      for _ in range(0, n):
        # get another user __u and response y from same scene
        __uId, y = self._getY(sceneX)
        
        __u = self.users[__uId]

        # another response by user u. x'
        sceneX_, x_ = self._getX(_u)

        # get y''
        y_ = self._getYprime(__u, sceneX_, sceneX)
        
        c2 = __u.getCluster()
       

        s1 = self.scores[clust][c2][x, y]
        s2 = self.scores[clust][c2][x_, y_]
        score.append(s1-s2)
      scores.append(sum(score) / n)
    return sum(scores)

  def clustScore(self, _u, opposingCuster, n):
    scs = []
    for idx, sceneX in enumerate(_u.scenes):
      x = _u.emotions[idx]
      score = []
      cnt = 0
      for _ in range(0, n):
        try:
          __uId, y  = self._getY_clust(sceneX, opposingCuster)
          __u = self.users[__uId]

          # another response by user u. x'
          sceneX_, x_ = self._getX(_u)

          # get y''
          y_ = self._getYprime(__u, sceneX_, sceneX)
          
          c1 = _u.getCluster()
          c2 = __u.getCluster()
        

          s1 = self.scores[c1][c2][x, y]
          s2 = self.scores[c1][c2][x_, y_]
          score.append(s1-s2)
          cnt += 1
        except:
          pass
      if cnt > 0:
        scs.append(sum(score) / cnt)
      else:
        return 0
    return sum(scs)
    
  def _getY(self, scene,  debug=False):
    othersRespondToIth = self.globalScene[scene]
    rIdx = np.random.randint(low=0, high=othersRespondToIth.shape[1])
    y_user = othersRespondToIth[0][rIdx]
    y_response = othersRespondToIth[1][rIdx]
    if debug: 
      print(y_user, y_response)

    return y_user, y_response

  def _getY_clust(self, scene, clust,  debug=False):
    othersRespondToIth = self.globalScene[scene]
    users, globalIndices, _ = np.intersect1d(othersRespondToIth[0], self.clusters[clust].users, return_indices=True)
    rIdx = np.random.choice(globalIndices)
    y_user = othersRespondToIth[0][rIdx]
    y_response = othersRespondToIth[1][rIdx]
    if debug: 
      print(y_user, y_response)

    return y_user, y_response

  def _getX(self, user, debug= False):
    rIdx = np.random.randint(low=0, high=user.scenes.shape[0])
    _u_x_scene = user.scenes[rIdx]
    _u_x_response = user.emotions[rIdx]

    if debug:
      print(_u_x_scene, _u_x_response)

    return _u_x_scene, _u_x_response

  def _getYprime(self, user, s1, s2, debug = False):
    rIdx = np.random.randint(low=0, high=user.emotions.shape[0])

    response = user.emotions[rIdx]
    scene = user.scenes[rIdx]

    while scene == s1 or scene == s2:
      rIdx = np.random.randint(low=0, high=user.emotions.shape[0])
      response = user.emotions[rIdx]
      scene = user.scenes[rIdx]
      if debug:
        print(scene, response)

    return response
        

class ScoreStruct:
  def __init__(self, struct):
    self.vectors = struct.vectors
    self.emotions = struct.emotions
    self.scores = [CorrelationStructure(self.emotions) for i in range(len(self.vectors))]


  def __getitem__(self, attr):
    return self.scores[attr]

  def getScores(self, method='standard'):
    if method == 'standard':
      self.standardScoring()
    elif method == 'threshold':
      self.thresholdScoring()
    elif method == 'binary':
      self.postiveOrNegative()
  
  def standardScoring(self): 
    for kidx, k in enumerate(self.vectors):
      # k == correlationStructure
      for ix,x in enumerate(k.map.keys()):
        px = k.prob[k.map[x], :].sum().sum()
        for iy,y in enumerate(k.map.keys()):
          py = k.prob[:, k.map[y] ].sum()
          pxy = px*py
          jpxy = k.prob[k.map[x]][k.map[y]]
          self.scores[kidx].vector[k.map[x]][k.map[y]] = 1 if jpxy > pxy else 0

  def thresholdScoring(self, threshold = -0.001):
    for kidx, k in enumerate(self.vectors):
      # k == correlationStructure
      for ix,x in enumerate(k.map.keys()):
        px = k.prob[k.map[x]].sum()
        for iy,y in enumerate(k.map.keys()):
          py = k.prob[k.map[y]].sum()
          pxy = px*py
          jpxy = k.prob[k.map[x]][k.map[y]]

          if (jpxy-pxy) > -0.001:
            self.scores[kidx].vector[k.map[x]][k.map[y]] = 1
          else:
            self.scores[kidx].vector[k.map[x]][k.map[y]] = 0


  # def postiveOrNegative(self):
  #   for kidx, k in enumerate(self.vectors):
  #     # k == correlationStructure
  #     for ix,x in enumerate(k.map.keys()):
  #       for iy,y in enumerate(k.map.keys()):\
  #         px = k.prob[:, k.map[x]].sum()
  #         py = k.prob[k.map[y], : ].sum()
  #         pxy = px*py
  #         jpxy = k.prob[k.map[x]][k.map[y]]

  #         self.scores[kidx].vector[k.map[x]][k.map[y]] = 1 if jpxy > pxy else -1