import random
import matplotlib.pyplot as plt
import math


class Ga():
  def __init__(self, numOfBattles, numPopultion, numOfSolders, numOfFittest, pMutation, numParent, k, Rf, mutationType, battleType, parentSelectionType):
    self.numOfBattles = numOfBattles
    self.numPopultion = numPopultion
    self.numOfSolders = numOfSolders
    self.numOfFittest = numOfFittest
    self.pMutation = pMutation
    self.numParent = numParent
    self.k = k
    self.avgFitness = []
    self.maxfitness = []
    self.Rf = Rf
    if battleType == 1:
      self.battle = self.battle1
    else:
      self.battle = self.battle2

    if mutationType == 1:
      self.mutation = self.mutation1
    else:
      self.mutation = self.mutation2

    if parentSelectionType == 1:
      self.parentSelection = self.tournomentSelection
    else:
      self.parentSelection = self.SusParentSelection

  def initializePopulation(self):
    population = []
    for _ in range(self.numPopultion): #for generating in number of population
      chrom = []
      usedSolders = 0
      for _ in range(self.numOfBattles - 1): #for generating in number of battles
        selectedSolders = random.randint(0, self.numOfSolders - usedSolders) #new solder gen should be less than remained solders 
        usedSolders += selectedSolders
        chrom.append(selectedSolders)
      chrom.append(self.numOfSolders - usedSolders) #for the last gen, we should use all remained solders
      population.append(chrom)

    # print (population)
    self.population = population

  def battle1(self, colonel1, colonel2):
    score1= 0
    score2 = 0
    for i in range(self.numOfBattles): #colonel1 battle againts colonel 2, 4 times, and result of each time calculate, and add to score
      if (colonel1[i] > colonel2[i]): # win 
        score1 += 2
      elif (colonel1[i] == colonel2[i]): #tie
        score1 += 1
        score2 += 1
      else:
        score2 += 2

    if score1 >= score2:
      return 1
    else:
      return 0

  def fitness(self, chrom, population):
    fit = 0
    for i in range(self.numPopultion): #the chrom has to battle againts all of the other chroms in population
      fit += self.battle(chrom, population[i])
    return fit - 1
  
  def calFitnessPopulation(self, pop):
    populationWithFitness = []
    for chrom in pop:
      populationWithFitness.append( ( chrom, self.fitness(chrom, pop) ) )
    return populationWithFitness

  def tournomentSelection(self): #tournoment with k(number of random selected parent for each iteration)
    selectedParent = []
    populationWithFitness = self.calFitnessPopulation(self.population)
    for _ in range(self.numParent): #as much as parent we want, we execute tournoment
      tournoment = []
      for _ in range(self.k): #choose k random parent in each iteration
        parent = random.choice(populationWithFitness)
        tournoment.append(parent)
      tournoment.sort(key=lambda tup: tup[1], reverse=True) #sort random selected parent in order to chooose the best of them
      selectedParent.append(tournoment[0][0]) #choose the best
    self.selectedParents = selectedParent

  def wiseOnepointCrossOver(self, parents):
    crossOverPoint = random.randint(1, self.numOfBattles - 1)
    children = []
    for i in range (0,2): #do following instructions twice for getting two child
      newChild =  parents[i][:crossOverPoint]  #getting first part from current index parent
      children.append(newChild)
      oppositParentIndex = 1 - i #the other index parent
      sumSolders = sum(newChild) #till now, how many solders we use
      
      for j in range(crossOverPoint, self.numOfBattles): #filling remained part
        newSolders = parents[oppositParentIndex][j] #num solders this gen
        sumSolders += newSolders #update used solders
        children[i].append(newSolders) #add new gen to child chromosome
      
      #sum solders might exceed num of solders (20) 
      usedSolders = sum(children[i])
      extraSolders = usedSolders - self.numOfSolders
      # print("extraSolders", extraSolders)
      if extraSolders > 0:
        h = 0
        while extraSolders > 0:
          if children[i][h] > 0:
            children[i][h] -= 1
            extraSolders -= 1
          h = (h + 1) % 4

      elif extraSolders < 0:
        h = 0
        while extraSolders < 0:
          children[i][h] += 1
          extraSolders += 1
          h = (h + 1) % 4

    return children

  def onePointCrossOver(self, parents): 
    crossOverPoint = random.randint(1, self.numOfBattles - 1)
    children = []
    for i in range (0,2): #do following instructions twice for getting two child
      newChild =  parents[i][:crossOverPoint]  #getting first part from current index parent
      children.append(newChild)
      oppositParentIndex = 1 - i #the other index parent
      sumSolders = sum(newChild) #till now, how many solders we use
      
      for j in range(crossOverPoint, self.numOfBattles - 1): #filling remained part
        remainedSolders = self.numOfSolders - sumSolders #how much solders does left to use
        newSolders = parents[oppositParentIndex][j] #num solders this gen
        if newSolders <= remainedSolders : #we have enough solders to use
          newS = newSolders #so we use as much as we needed
        else: #we dont have as much as newSolders number, solders left to use
          newS = remainedSolders #so we use all we have left
        sumSolders += newS #update used solders
        children[i].append(newS) #add new gen to child chromosome
      
      #for last battle we should use excatly as much as remained solders
      children[i].append(self.numOfSolders - sumSolders)

    return children

  def applyCrossOver(self):
    numSelected = len(self.selectedParents)
    offSprings = []
    for i in range(0, numSelected, 2):
      offSprings.extend(self.wiseOnepointCrossOver(self.selectedParents[i:i+2])) 
    self.offSprings = offSprings

  def mutation1(self, child):
    i = random.randint(0, len(child) - 1)
    j = random.randint(0, len(child) - 1)
    child[i], child[j] = child[j], child[i]
  
  def mutation2(self, child):
    i = random.randint(0, len(child) - 1)
    j = random.randint(0, len(child) - 1)
    if child[i] > 0:
      child[i] = child[i] - 1
      child[j] = child[j] + 1
    elif child[j] > 0:
      child[i] = child[i] + 1
      child[j] = child[j] - 1

  def applyMutation(self):
    for child in self.offSprings:
      p = random.uniform(0.0, 1.0)
      if (p <= self.pMutation): #since 1/L == 1/4 == 0.25, mutation probability should be less than 0.25 
        self.mutation(child)

  def survivalSelection(self):
    populationWithFitness = self.calFitnessPopulation(self.population)
    #print("populationWithFitness", populationWithFitness, "\n")
    populationWithFitness.sort(key=lambda tup: tup[1], reverse=True) #sort population to choose 10% fittest
    #print("populationWithFitness", populationWithFitness, "\n")
    fittest = [item[0] for item in populationWithFitness[0:self.numOfFittest] ] 
    #print("fittest", fittest, "\n")
    newPopulationWithFitness = self.calFitnessPopulation(self.offSprings)
    #print("newpopwithfit", newPopulationWithFitness, "\n")
    newPopulationWithFitness.sort(key=lambda tup: tup[1]) #sort population to choose 10% fittest
    #print("newpopwithfit", newPopulationWithFitness, "\n")
    leastFittestOfNewPopulation = newPopulationWithFitness[0:self.numOfFittest]
    #print("least", leastFittestOfNewPopulation, "\n")
    notLeastFittestOfNewPopulation = [item[0] for item in newPopulationWithFitness[self.numOfFittest:]]
    #print("not least", notLeastFittestOfNewPopulation, "\n")
    elitismUnionNewPopulationWithFitness = self.calFitnessPopulation(fittest + notLeastFittestOfNewPopulation)
    #print("elitismwithnewpop", elitismUnionNewPopulationWithFitness, "\n")
    for i in range(self.numOfFittest):
      val = elitismUnionNewPopulationWithFitness[i][1] #fitness of elitism
      for x in leastFittestOfNewPopulation: 
        if val < x[1]: 
            elitismUnionNewPopulationWithFitness[i] = x
            break
    self.population = [item[0] for item in elitismUnionNewPopulationWithFitness] 
    # print("self.population", self.population, "\n")
    
  def plot(self, title):
    if len(self.maxfitness) == 1:
      plt.scatter(x=0, y=self.maxfitness[0], color = "#00ace6", label = "max fitness")
      plt.scatter(x=0, y=self.avgFitness[0], color = "#9933ff", label = "avg fitness")
      plt.xlabel('iteration') 
      plt.ylabel('fitness')
      plt.title(title) 
      plt.legend()
      plt.show()
      return
    plt.plot(self.iterations, self.avgFitness, color = "#9933ff", label = "avg fitness")
    plt.plot(self.iterations, self.maxfitness, color = "#00ace6", label = "max fitness")
    plt.xlabel('iteration') 
    plt.ylabel('fitness')
    plt.title(title) 
    plt.legend()
    plt.show()

  def checkForSolution(self):
    newPop = self.calFitnessPopulation(self.population)
    newPop.sort(key=lambda tup: tup[1], reverse=True)
    avg = sum(n for _, n in newPop) / self.numPopultion
    self.avgFitness.append(avg)
    self.maxfitness.append(newPop[0][1])
    return newPop

  def SusParentSelection(self):
    parentsWithFitness = self.calFitnessPopulation(self.population)
    parentsWithFitness.sort(key=lambda tup: tup[1])
    sum1 = sum(n for _, n in parentsWithFitness)
    selected = []
    comulative = 0
    for i in range(len(parentsWithFitness)):
      comulative += parentsWithFitness[i][1] / sum1
      parentsWithFitness[i] = (parentsWithFitness[i][0], comulative )
    currentMember = 0
    i = 0
    r = random.uniform(0, 1/self.numParent)
    while (currentMember < self.numParent):
      while (r <= parentsWithFitness[i][1]):
        selected.append(parentsWithFitness[i][0])
        r += (1/self.numParent)
        currentMember += 1
      i += 1
    self.selectedParents = selected

  def battle2(self, colonel1, colonel2):
    print(colonel1, colonel2)
    score1= 0
    score2 = 0
    extraSolders = 0
    Rf = self.Rf
    c1 = colonel1[:]
    for i in range(self.numOfBattles): #c1 battle againts colonel 2, 4 times, and result of each time calculate, and add to score
      score1 += 1
      if (c1[i] > colonel2[i]): # win 
        score1 += 2
        e = math.trunc(Rf * (c1[i] - colonel2[i] - 1))
        if i != 3:
          extraSolders += e
          c1[i] -= e
        else:
          c1[i] += extraSolders
      else: #need extra
        c1[i] = c1[i] +  math.trunc(extraSolders / (4 - i))
        extraSolders -= math.trunc(extraSolders / (4 - i))
        if (c1[i] > colonel2[i]): # win 
          score1 += 2
          e = math.trunc(Rf * (c1[i] - colonel2[i] - 1))
          if i != 3:
            extraSolders += e
            c1[i] -= e
          else:
            c1[i] += extraSolders
        elif (c1[i] == colonel2[i]): #tie
          score1 += 1
          score2 += 1
        else:
          score2 += 2
    print(c1)
    if score1 >= score2:
      return 1
    else:
      return 0

  def main(self):
    self.initializePopulation()
    for i in range(100):
      newPop = self.checkForSolution()
      if newPop[0][1] == 49:
        self.iterations = list(range(0, i+1))
        print('solution found within', i, 'iterations') 
        return newPop
      self.parentSelection()
      self.applyCrossOver()
      self.applyMutation()
      self.survivalSelection()
    self.iterations = list(range(0, i+1))
    print ('no solution found within', i, 'iterations')

# for _ in range(3):
#   ga1 = Ga(numOfBattles=4, numPopultion=50, numOfSolders=20, numOfFittest=5, pMutation=0.2, numParent=50, k=5, Rf=0, mutationType=1, battleType=1, parentSelectionType=1)
#   print('first Implementation')
#   solution = ga1.main()
#   if solution != None:
#     print ('best strategy is: ', solution[0][0])
#     print ('population with fitness: ','\n' , solution)
#   ga1.plot("first Implementation")

# for _ in range(3):
#   ga2 = Ga(numOfBattles=4, numPopultion=50, numOfSolders=20, numOfFittest=5, pMutation=0.2, numParent=50, k=5, Rf=0, mutationType=2, battleType=1, parentSelectionType=1)
#   print("Implement different mutation operator")
#   solution = ga2.main()
#   if solution != None:
#     print ('best strategy is: ', solution[0][0])
#     print ('population with fitness: ','\n' , solution)
#   ga2.plot("Implement different mutation operator")

# for _ in range(3):
#   ga3 = Ga(numOfBattles=4, numPopultion=50, numOfSolders=20, numOfFittest=5, pMutation=0.2, numParent=50, k=5, Rf=0, mutationType=1, battleType=1, parentSelectionType=2)
#   print("Implement different selection mechanism")
#   solution = ga3.main()
#   if solution != None:
#     print ('best strategy is: ', solution[0][0])
#     print ('population with fitness: ','\n' , solution)
#   ga3.plot("Implement different selection mechanism")

# for _ in range(3):
#   ga4 = Ga(numOfBattles=4, numPopultion=50, numOfSolders=20, numOfFittest=5, pMutation=0.2, numParent=50, k=5, Rf=1, mutationType=1, battleType=2, parentSelectionType=1)
#   print('Implement consider redistributing the soldiers')
#   solution = ga4.main()
#   if solution != None:
#     print ('best strategy is: ', solution[0][0])
#     print ('population with fitness: ','\n' , solution)
#   ga4.plot("Implement consider redistributing the soldiers")