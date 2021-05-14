from src.utils import Cluster, Scenes, Users, User
import pandas as pd
import numpy as np
import math
import random



class K_Mean:
  def __init__(self, _df, _K):
    self.df = _df
    self.emotions = self.df.emotion.unique()
    self.emotionMap = {e: idx for idx, e in enumerate(self.emotions )}
    self.M = self.emotions.shape[0]
    self.K = _K
    self.uniqueUsers = self.df.user.unique()

    # create hash values for contents and scenes and assign as index
    self.df['hash'] = self.df.apply(lambda x: hash((x.sceneIdx, x.contentIdx)), axis=1)

    userInfo = Users(self.df, self.uniqueUsers)
    self.globalScene = Scenes(self.df, self.uniqueUsers)


    self.users = {}
    for ithU in self.uniqueUsers:
      self.users[ithU] = User(self.K, self.emotions, userInfo[ithU], ithU)
    self.clusters = []
    self.uInClust = set()
  
  def oneVeresusAll(self,epochs, n=40, multiplier=3):
    self.initializeClusters(n=n, multiplier=multiplier, debug=False)
    
    for i in range(epochs):
      self.cUsers(self.uniqueUsers, scenes='all')
      self.assignClusters(method='all', debug=False)
      self.updateCentroid2()


  def initializeClusters(self, n=40, multiplier=3, debug=False):
    # get users w/lots of responses and high entropy
    usersRemain  = self.getKUsers_entropy(n, self.K * multiplier)

    #get jp matrices for users
    self.calculate1vAll(usersRemain)

    #calculate the K most heterogeneous centers
    points = self.getTopCenters(usersRemain)


    # assign K users to cluster
    for k in range(self.K):
      self.clusters.append(Cluster(self.K, self.emotions, self.df, [points[k]], k ))
      self.users[points[k]].setCluster(k)
      self.uInClust.add(points[k])
    

    # update centroid so user is now centroid of cluster
    self.updateCentroid()
    # get the scenes and corresponding users that the K users currently in cluster have all responded to
    usersToUpdate, sceneToUpdate = self.clustSceneIntersection()
    
    #calculate all users that have responded to scenes in the cluster
    self.cUsers(users=usersToUpdate, scenes=sceneToUpdate)
    self.cUsers(users=points, scenes=sceneToUpdate)
    
    self.assignClusters(method='selection', debug=debug, users=usersToUpdate)

    self.updateCentroid()


  

  def calculate1vAll(self, users ):    
    for ithUser in users:
      _u = self.users[ithUser]
      _u.struct.reset()
      scenes = _u.scenes
      u_responses = _u.emotions
      for idx, ithScene in enumerate(scenes):
        u_response = u_responses[idx]
        o_responses = self.globalScene[ithScene][1]

        for k in range(self.K):
          _u.updateStruct(k, u_response, o_responses)
        

            
  def setUserClusters(self,_u, u_emotion, scene):
    for k in self.clusters:
      users_k = k.users
      responses_k = k.sceneInfo[scene][-1]
      _u.updateStruct( k.clusterId , u_emotion, responses_k)
  
#   def pcUsers(self, users, scenes='all', debug=False, parallel=False ):
#     p = Pool(processes=2)
#     keys, values= zip(*self.users.items())
#     processed_values = p.map( self.pcessUser, values)
#     p.close()
#     p.join()
#     return processed_values
                                   

  def pcessUser(self, _u):
    _u.struct.reset()
    for sceneIdx, scene in enumerate(_u.scenes):
      u_emotion = _u.emotions[sceneIdx]
      if type(scenes) != list:
        self.setUserClusters(_u, u_emotion, scene)
      elif scene in scenes:
        self.setUserClusters(_u, u_emotion, scene)

  def cUsers(self, users, scenes='all', debug=False, parallel=False ):
    for ithUser in users:
      _u = self.users[ithUser]
      _u.struct.reset()
      for sceneIdx, scene in enumerate(_u.scenes):
        u_emotion = _u.emotions[sceneIdx]
        if type(scenes) != list:
          self.setUserClusters(_u, u_emotion, scene)
        elif scene in scenes:
          self.setUserClusters(_u, u_emotion, scene)



  def calculateUsers(self, method='inCluster', debug=False, **kwargs):
    if method == 'all':
      self.cAll(debug=debug, parallel=False)
    elif method == 'sceneAndUser' and 'users' in kwargs and 'scenes' in kwargs:
      users = kwargs['users']
      scenes = kwargs['scenes']
    else:
      print("Calculate Users Error")
    print("Done", method)




  def assignClusters(self, method='all', debug=False, **kwargs):
    if method == 'all':
      users = self.uniqueUsers
    elif method == 'selection' and 'users' in kwargs:
      users = kwargs['users']
    
    newUsersInCluster = [[] for i in range(self.K)]

    # update user cluster assignment and keep track of new users in cluster
    for user in users:
      _u = self.users[user]
      _u.struct.getProb()
      clustToUserNorms = np.zeros(self.K)

      for idx, k in enumerate(self.clusters):
        clustToUserNorms[idx] = k.struct.AvgL1_Norm(_u.struct)
      
      # find the cluster index with lowest norm
      kAssignIdx = np.argmin(clustToUserNorms)
      
      # set cluster for user _u to cluster with min norm
      _u.setCluster(kAssignIdx)

      # assign user to cluster at [kAssignIdx] 
      newUsersInCluster[kAssignIdx].append(user)

      # update set (keeps track of users that need a cluster)
      self.uInClust.add(_u.id)      
  
    for i,_k in enumerate(self.clusters):
      _k.setUsers( newUsersInCluster[i])

 
   
  def updateCentroid(self, debug=False):
    for clust in self.clusters:
      clust.updateCentroid(self.users)
  def updateCentroid2(self):
    for c1 in self.clusters:
      for c2 in self.clusters:
        c1.updateCentroid2(c2, self.users)

  def getTopCenters(self, usersRemain):
      # randomly choose one from users to be k=1 cluster
      k1idx, k1 = random.choice(list(enumerate(usersRemain)))
      points = [k1]
      usersRemain.pop(k1idx)

      # find remaining clusters by maximizing distance
      for kth in range(self.K - 1):
        maxForK = []
        for uIdx, user in enumerate(usersRemain):
          # maximize distance from those in points
          collectiveDist = 0
          for p in points:
            collectiveDist += self.users[user].struct.AvgL1_Norm(self.users[p].struct)
          maxForK.append(collectiveDist)
        argMaxU = np.argmax(np.array(maxForK))
        points.append(usersRemain[argMaxU])
        usersRemain.pop(argMaxU)
      
      return points

  def clustSceneIntersection(self):
    listofScenes = []
    for i in range(self.K):
      listofScenes.append(self.users[self.clusters[i].users[0]].scenes)

    intersection = listofScenes[0]
    for i in range(1, self.K):
      intersection = np.intersect1d(intersection, listofScenes[i])

    totUsers = []
    for scenes in intersection:
      totUsers.append(np.unique(self.globalScene[scenes][0]))
    totUsers = np.array(totUsers)

    union = totUsers[0]
    for i in range(1, len(intersection)):
      union = np.union1d(union, totUsers[i])
    
    # return users (union) that have responded to scenes in intersection
    return union, intersection

  
  def getKUsers_entropy(self, minScenes, nUsers):
    def Sort_Tuple(tup): 
      tup.sort(key = lambda x: x[1]) 
      return tup 
    
    # gets most responded to scenes to ensure every user selected shares at least one scene
    highestScenes = self.df.groupby('hash').agg({'user':pd.Series.nunique}).sort_values(by='user', ascending=False).reset_index().loc[:5, 'hash'].to_numpy()
    kk12 = self.df[self.df['user'].isin(np.unique(self.globalScene[highestScenes[0]][0]))]


    filterUsers = filterSceneCount(kk12, minScenes)
    ar = []
    for us in filterUsers:
      t = np.unique(self.users[us].emotions, return_counts=True)
      s_e = sum([(i / sum(t[1])) * math.log2((i / sum(t[1]))) for i in t[1]]) * -1
      ar.append((us, s_e))

    # get users w. highest entropy
    sortedEntrop = Sort_Tuple(ar)[-nUsers:]
    r = []
    for i in sortedEntrop:
      r.append(i[0])
      
    return r



def filterSceneCount(df, minScenes):
  users = df.groupby(df.user).agg({"hash": pd.Series.nunique})
  mask = users.apply(lambda x: x.hash >= minScenes, axis=1).reset_index(name='bb')
  kk = df.merge(mask,on='user',how='left')
  k3 = kk.loc[kk.bb == True, :]
  return k3.user.unique()
  