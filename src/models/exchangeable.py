def jointProbability(M):
  jp = []
  for i in range(0, M):
    row = []
    for x in range(0, M):
      NUM = 1/M if i == x else 0
      row.append(NUM)
    jp.append(row)
  
  return np.array(jp) 
  
def countMatrix(M):
  return np.array([[0 for i in range(0,M)] for i in range(0, M)])   


def pairs(*lists):
  for t in combinations(lists, 2):
      for pair in product(*t):
          yield pair
def proccessEmotionData(media, content, timestampColumnName = 'timestamp', sceneIdxName = 'sceneIdx'):
    df = pd.DataFrame(media, columns=["user", "timestamp", "emotion" ])
    df[sceneIdxName] = df.apply(lambda x: content.getSceneIndex(x[timestampColumnName]), axis=1)
    return df

'''
@params: pairs: pair of emotions in format [[emotion1, emotion2],.....]
        countMatrix 
@return updateCountMatrix
'''
def updateCountMatrix(pairs, countMatrix, eMap):
  for i in pairs:
    emotionOneIDX, emotionTwoIDX = eMap[i[0]], eMap[i[1]]
    countMatrix[emotionOneIDX][emotionTwoIDX] += 1
    countMatrix[emotionTwoIDX][emotionOneIDX] += 1
    class ExchangeableUser:
  def __init__(self, df):
    self.df = df
    self.emotions = self.df.emotion.unique()
    self.emotionMap = {e: idx for idx, e in enumerate(self.emotions )}
    self.M = self.emotions.shape[0]

    # get unique users for random sampling
    self.users = self.df.user.unique()
    self.nUsers = self.users.shape[0]

    # get unique scenes
    self.content = self.df.contentIdx.unique()
    self.nContent = self.content.shape[0]

    # matrices
    self.jp = jointProbability(self.M)
    self.count = countMatrix(self.M)

    self.getTopUsers()



  def generateJP(self, B=100, method='top' ):
    errors = 0 # for error handling
    

    for i in range(0, B):

      if method == 'top':
        contentId = np.random.choice(self.content, 1)[0]
        
        sceneId = np.random.choice(self.top[contentId].scenes, size=1)[0]

        responses = self.df[(self.df.contentIdx == contentId) & (self.df.sceneIdx == sceneId)]

        respondedToScene = responses.user.unique()

      try:

        # #currently sampling with replacement --> might need to change
        randomUsers = np.random.choice(respondedToScene,2, replace=True) 

        # # create list of emotions recorded from this scene for user i
        i1 = np.array(responses[responses.user == randomUsers[0]].emotion)

        # # create list of emotions recorded from this scene for user i'
        i2 = np.array(responses[responses.user == randomUsers[1]].emotion)

        self.updateCountMatrix(pairs(i1, i2),  self.emotionMap)

        # calculate new joint probability matrix?
        self.jp = self.count / self.count.sum()

      except Exception as inst:
        errors += 1
    
    print(errors, "samples did not have any responses")
    return self.jp
  

  def V1score(self, heatMap = True):

    sums = np.sum(emoji.jp, axis=1)
    score = np.zeros([self.M, self.M])

    for x in range(0, self.jp.shape[0]):
      pOfX = sums[x]

      for y in range(0, self.jp.shape[1]):
        pOfY = sums[y]
        probXY = pOfX * pOfY

        if self.jp[x,y] > probXY:
          score[x, y] = 1

    self.score = score

    if heatMap: 
      return sns.heatmap(pd.DataFrame(score, columns=self.emotions, index=self.emotions))


class ExchangeableUser(ExchangeableUser):
  def displayEmotionCounts(self):
    return sns.barplot(x=self.df.emotion.value_counts().index, y=self.df.emotion.value_counts().values).set_title("Total Emotion Count All Content")
  def displayJP(self):
    return sns.heatmap(pd.DataFrame(self.jp, columns=self.emotions, index=self.emotions))


class ExchangeableUser(ExchangeableUser):
  '''
  @params: pairs: pair of emotions in format [[emotion1, emotion2],.....]
          countMatrix 
  @return updateCountMatrix
  '''
  def updateCountMatrix(self, pairs, eMap):
    for i in pairs:
      emotionOneIDX, emotionTwoIDX = eMap[i[0]], eMap[i[1]]
      self.count[emotionOneIDX][emotionTwoIDX] += 1
      self.count[emotionTwoIDX][emotionOneIDX] += 1

  def resetMatrices(self):
    self.jp = jointProbability(self.M)
    self.count = countMatrix(self.M)


def randomUser(df, scene, content , user):
  tempDf = df[(df.contentIdx == content) & (df.sceneIdx == scene) & (df.user != user)]
  id = np.random.choice(tempDf.user.unique(), 1)[0]
  emotion = tempDf[tempDf.user == id].sample(n=1).emotion.to_numpy()[0]

  return emotion ,id 



def getXPrime(df, content, user):
  tempDf = df[(df.contentIdx != content) & (df.user == user)].reset_index()
  random = np.random.randint(low=0, high=tempDf.shape[0])
  randomUser = tempDf.iloc[random, :]

  return randomUser['emotion'], randomUser['contentIdx']



def getYprime(df, user, content):

  tempDf = df[(df.contentIdx != content[0]) & (df.contentIdx != content[1]) & (df.user == user)]
  random = np.random.randint(low=0, high=tempDf.shape[0])
  randomUser = tempDf.iloc[random, :]
  
  return randomUser['emotion']

def getDfWtwoContentResponses(df, minResponse):
  k = df
  users = df.groupby('user').contentIdx.unique()
  mask = users.apply(lambda x: x.shape[0] >= minResponse)
  kk = k.join(mask, on='user', how='left', rsuffix='_r')
  k3 = kk.loc[kk.contentIdx_r == True, kk.columns !='contentIdx_r']
  return k3, k3.user.unique()

class ExchangeableUser(ExchangeableUser):
  def getTopUsers(self):
    top = {}
    for i in self.content:
      top[i] = ScenePriority(self.df, i, 6)

    self.top = top

class ExchangeableUser(ExchangeableUser):
  
  def getInteresction(self, debug=False, sample=False):

    newDf, uniqueUser = getDfWtwoContentResponses(self.df, 2)

    if sample:
      # get users -- for speed purposes do sample
      sampleOfUsers = np.random.choice(uniqueUser, size=sample)
    else:
      sampleOfUsers = uniqueUser

    userScenes = {}

    for ithUser in sampleOfUsers:
      userDf = self.df[self.df.user == ithUser]
      scenesResponded = userDf.contentIdx.unique()

      scenes = []
      for ithContent in scenesResponded:
        #scenes responded to on ithContent by ithUser
        scenesByUser = userDf[userDf.contentIdx == ithContent].sceneIdx.unique()
        topScenes = self.top[ithContent].scenes 
        
        # get intersection of topscenes and scenes by user
        intersection = np.intersect1d(scenesByUser, topScenes)

        # debug
        if debug:
          print(ithUser)
          print("\t",ithContent," : ", intersection )

        for s in intersection:
          #add content scene pair to user
          scenes.append((ithContent, s))
      userScenes[ithUser] = scenes
    return userScenes, newDf
  
  def userScores(self, nSamples=20, debug=False):

    userScenes, newDf = self.getInteresction(debug=debug)
    userScores = {}


    for ithUser in userScenes:
      arr = np.array(userScenes[ithUser])
      len = arr.shape[0]

      userDf = newDf[newDf.user == ithUser]

      # if user has responded to a top scene
      if len > 0:
        idxs = np.random.randint(arr.shape[0], size=nSamples)
        sample = arr[idxs, :]
        

        for ithSample in sample:
          c1 = ithSample[0]
          s1 = ithSample[1]

          rOne = userDf[(userDf.contentIdx == c1) &( userDf.sceneIdx == s1)].emotion      

          # if there are > 1 response, pick random scene
          if rOne.shape[0] == 1:
            eOne = rOne.iloc[0]
          else:
            eOne = np.random.choice(rOne, size=1)[0]
          
        

          try: 
            u2eOne, u2 = randomUser(newDf, s1, c1, ithUser)
          except Exception as inst:
            print(inst)
          
          try:
            eTwo, c2 = getXPrime(userDf, c1, ithUser)
            
          except Exception as inst:
            print(inst)

          try:
            u2eTwo = getYprime(newDf, u2, [c2, c1])
          
          except Exception as inst:
            print(inst)



          sxy = self.score[self.emotionMap[eOne]][self.emotionMap[u2eOne]]
          sxyPrime = self.score[self.emotionMap[eTwo]][self.emotionMap[u2eTwo]]
          tempScore = sxy - sxyPrime

          if ithUser in userScores:
            userScores[ithUser] += tempScore
          else:
            userScores[ithUser] = tempScore
          
          if debug:
            print(ithUser)
            print("\t", f"""R({int(ithUser)}, {int(c1)},{int(s1)})= x = """, eOne)
            print("\t", f"""R({int(u2)}, c', s')= y =""", u2eOne)
            print("\t", f"""R({int(ithUser)}, {c2}, s')= x' =""", eTwo)
            print("\t", f"""R({int(u2)}, c'' , s'')= y'' =""", u2eTwo)
            print("\t \t", f"""S(x,y) = {sxy} S(x',y'') = {sxyPrime} score = {tempScore}""")
    self.userScores = userScores
    return userScores



          
      








