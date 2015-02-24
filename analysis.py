#! /usr/bin/env python
# encoding: utf-8

from datetime import timedelta
import geometry
import Levenshtein
import MantelTest
import matplotlib.pyplot as plt
import numpy
import page
from random import shuffle
from scipy import log, log2, mean, polyfit, sqrt, stats, std
import scipy.cluster
import re

chain_codes = [["A", "B", "C", "D"], ["E", "F", "G", "H"], ["I", "J", "K", "L"]]

#############################################################################
# MEASURE LEARNABILITY: CALCULATE TRANSMISSION ERROR AND THEN COMPARE THE
# VERIDICAL SCORE TO A MONTE CARLO SAMPLE

def learnability(experiment, chain, generation, simulations=100000):
  words_A = getWords(experiment, chain, generation, "s")
  words_B = getWords(experiment, chain, generation-1, "s")
  x = meanNormLevenshtein(words_A, words_B)
  m, sd = MonteCarloError(words_A, words_B, simulations)
  z = (m-x)/sd
  return x, m, sd, z

# CALCULATE THE TRANSMISSION ERROR BETWEEN TWO CONSECUTIVE PARTICIPANTS

def transmissionError(experiment, chain, generation):
  words_A = getWords(experiment, chain, generation, "s")
  words_B = getWords(experiment, chain, generation-1, "s")
  return meanNormLevenshtein(words_A, words_B)

# GIVEN TWO SETS OF STRINGS, SHUFFLE ONE SET OF STRINGS n TIMES. COMPUTE THE
# MEAN NORMALIZED LEVENSHTEIN DISTANCE FOR EACH SHUFFLING AND RETURN THE MEAN
# AND STANDARD DEVIATION OF THE COMPUTED SCORES

def MonteCarloError(strings1, strings2, simulations):
  distances = []
  for i in xrange(0, simulations):
    shuffle(strings1)
    distances.append(meanNormLevenshtein(strings1, strings2))
  return mean(distances), std(distances)

# CALCULATE THE MEAN NORMALIZED LEVENSHTEIN DISTANCE BETWEEN TWO SETS OF STRINGS

def meanNormLevenshtein(strings1, strings2):
  total = 0.0
  for i in range(0, len(strings1)):
    ld = Levenshtein.distance(strings1[i], strings2[i])
    total += ld/float(max(len(strings1[i]), len(strings2[i])))
  return total/float(len(strings1))

#############################################################################
# MEASURE LEARNABILITY IN TRAINING: CALCULATE THE MEAN NORMALIZED LEVENSHTEIN
# DISTANCE FOR A SPECIFIC INDIVIDUAL'S TRAINING RESULTS

def trainingError(experiment, chain, generation, subject=''):
  if subject == 'A' or subject == 'B':
    filename = 'logSub' + subject
  else:
    filename = 'log'
  data = load(experiment, chain, generation, filename)
  words_A = [data[x][0] for x in range(5,53)]
  words_B = [data[x][1] for x in range(5,53)]
  x = meanNormLevenshtein(words_A, words_B)
  return x

#############################################################################
# COUNT THE NUMBER OF UNIQUE WORDS FOR GIVEN PARTICIPANT

def uniqueStrings(experiment, chain, generation):
  dynamic_data = load(experiment, chain, generation, "d")
  stable_data = load(experiment, chain, generation, "s")
  dynamic_words = [row[0] for row in dynamic_data]
  stable_words = [row[0] for row in stable_data]
  combined_words = dynamic_words + stable_words
  return len(set(dynamic_words)), len(set(stable_words)), len(set(combined_words))

#############################################################################
# GET TRANSMISSION ERROR RESULTS FOR ALL CHAINS IN AN EXPERIMENT

def allTransmissionErrors(experiment):
  results = []
  for chain in chain_codes[experiment-1]:
    scores = []
    for generation in range(1, 11):
      try:
        score = transmissionError(experiment, chain, generation)
        scores.append(score)
      except:
        scores.append("N/A")
    results.append(scores)
  return results

#############################################################################
# GET LEARNABILITY RESULTS FOR ALL CHAINS IN AN EXPERIMENT

def allLearnability(experiment, sims=100000):
  results = []
  for chain in chain_codes[experiment-1]:
    print "Chain " + chain + "..."
    scores = []
    for generation in range(1, 11):
      try: 
        score = learnability(experiment, chain, generation, sims)[3]
        scores.append(score)
      except:
        scores.append("N/A")
    results.append(scores)
  return results

#############################################################################
# GET TRANSMISSION ERROR RESULTS FOR ALL CHAINS IN AN EXPERIMENT

def allTrainingErrors(experiment):
  results = []
  for chain in chain_codes[experiment-1]:
    scores = []
    for generation in range(1, 11):
      try:
        score = trainingError(experiment, chain, generation)
        scores.append(score)
      except:
        scores.append("N/A")
    results.append(scores)
  return results

#############################################################################
# CALCULATE COMMUNICATIVE ACCURACY

def commAccuracy(experiment, chain, generation):
  accuracy = 0
  dynamic_set = load(experiment, chain, generation, "d")
  for item in dynamic_set:
    coord_target = item[1] + ',' + item[2] + ',' + item[3]
    coord_select = item[5] + ',' + item[6] + ',' + item[7]
    if coord_target == coord_select:
      accuracy += 1
  stable_set = load(experiment, chain, generation, "s")
  for item in stable_set:
    coord_target = item[1] + ',' + item[2] + ',' + item[3]
    coord_select = item[5] + ',' + item[6] + ',' + item[7]
    if coord_target == coord_select:
      accuracy += 1
  return accuracy

#############################################################################
# PLOT MEANS FOR EACH GENERATION WITH ERROR BARS (95% CI)

def plotMean(matrix, start=1, y_label="Score", miny=0.0, maxy=1.0, conf=False, conf_bonf=False):
  fig, ax = plt.subplots(figsize=plt.figaspect(0.625))
  m = len(matrix)
  n = len(matrix[0])
  if conf == True:
    ax.plot(range(-1,n+2), [1.959964] * (n+3), color='gray', linestyle=':')
    ax.plot(range(-1,n+2), [-1.959964] * (n+3), color='gray', linestyle=':')
  if conf_bonf == True:
    ax.plot(range(-1,n+2), [2.734369] * (n+3), color='k', linestyle='--')
    ax.plot(range(-1,n+2), [-2.734369] * (n+3), color='k', linestyle='--')
  means = []
  errors = []
  for i in range(0,n):
    column = [row[i] for row in matrix if row[i] != None]
    means.append(mean(column))
    errors.append((std(column)/sqrt(m))*1.959964)
  xvals = range(start, n+start)
  (_, caps, _) = ax.errorbar(xvals, means, yerr=errors, color='k', linestyle="-", linewidth=2.0, capsize=5.0, elinewidth=1.5)
  for cap in caps:
    cap.set_markeredgewidth(2)
  labels = range(start, start+n)
  plt.xticks(xvals, labels, fontsize=14)
  plt.yticks(fontsize=14)
  plt.xlim(start-0.5, n+start-0.5)
  plt.ylim(miny, maxy)
  plt.xlabel("Generation number", fontsize=22)
  plt.ylabel(y_label, fontsize=22)
  plt.show()

#############################################################################
# PLOT ALL CHAINS FROM A DATA MATRIX

def plotAll(matrix, start=1, x_label="Generation number", y_label="Score", miny=0.0, maxy=1.0, conf=False, conf_bonf=False):
  fig, ax = plt.subplots(figsize=plt.figaspect(0.625))
  colours = ["#2E578C","#5D9648","#E7A13D","#BC2D30"]
  plt.rcParams['font.sans-serif']='Arial'
  n = len(matrix[0])
  xvals = range(start, n+start)
  if conf == True:
    ax.plot(range(0,n+1), [1.959964] * (n+1), color='gray', linestyle=':')
    ax.plot(range(0,n+1), [-1.959964] * (n+1), color='gray', linestyle=':')
  if conf_bonf == True:
    ax.plot(range(0,n+1), [2.734369] * (n+1), color='k', linestyle='--')
    ax.plot(range(0,n+1), [-2.734369] * (n+1), color='k', linestyle='--')
  for i in range(0,len(matrix)):
    x_vals = range(start, len(matrix[i])+start)
    ax.plot(x_vals, matrix[i], color=colours[i], linewidth=2.0)
  labels = range(start, start+n)
  plt.xlim(start, n+start-1)
  plt.ylim(miny, maxy)
  plt.xticks(xvals, labels, fontsize=14)
  plt.yticks(fontsize=14)
  plt.xlabel(x_label, fontsize=22)
  plt.ylabel(y_label, fontsize=22)
  plt.show()

#############################################################################
# RUN ALL THREE STATS

def runStats(data_matrix, hypothesis="d", include_gen_zero=True):

  if include_gen_zero == False:
    matrix = []
    for row in data_matrix:
      matrix.append([row[i] for i in range(1,len(row))])
  else:
    matrix = data_matrix

  page_results = page.ptt(matrix, hypothesis)
  print('''Page's trend test
L = %s, m = %s, n = %s, p %s, one-tailed''' % page_results)
  print("")

  pearson_results = pearson(matrix)
  print('''Correlation between scores and generation numbers
r = %s, n = %s, p = %s, one-tailed''' % pearson_results)
  print("")

  student_results = student(matrix, hypothesis)
  print('''Paired t-test between first and last generations
diff = %s, t (%s) = %s, p = %s, one-tailed''' % student_results)

#############################################################################
# CORRELATE A MATRIX OF RESULTS WITH GENERATION NUMBERS

def pearson(matrix):
  scores = matrix2vector(matrix)
  gen_nums = range(1,len(matrix[0])+1)*len(matrix)
  test = stats.pearsonr(scores, gen_nums)
  return test[0], len(scores), test[1]/2.0

#############################################################################
# PAIRED T-TEST BETWEEN FIRST AND LAST GENERATIONS

def student(matrix, hypothesis):
  a = [row[0] for row in matrix]
  b = [row[len(matrix[0])-1] for row in matrix]
  if hypothesis == "ascending" or hypothesis == "a":
    test = stats.ttest_rel(b, a)
    diff = (float(sum(b))/len(b)) - (float(sum(a))/len(a))
  if hypothesis == "descending" or hypothesis == "d":
    test = stats.ttest_rel(a, b)
    diff = (float(sum(a))/len(a)) - (float(sum(b))/len(b))
  return diff, len(a)-2, test[0], test[1]/2.0

#############################################################################
# LOAD RAW DATA FROM A DATA FILE INTO A DATA MATRIX

def load(experiment, chain, generation, set_type):
  filename = "Data/" + str(experiment) + "/" + chain + "/" + str(generation) + set_type
  f = open(filename, 'r')
  data = f.read()
  f.close()
  rows = data.split("\n")
  matrix = []
  for row in rows:
    cells = row.split("\t")
    matrix.append(cells)
  return matrix

#############################################################################
# LOAD IN THE WORDS FROM A SPECIFIC SET FILE

def getTriangles(experiment, chain, generation, set_type):
  if set_type == "c":
    data = load(experiment, chain, generation, "d") + load(experiment, chain, generation, "s")
  else:
    data = load(experiment, chain, generation, set_type)
  triangles = []
  for row in data:
    x1, y1 = row[1].split(',')
    x2, y2 = row[2].split(',')
    x3, y3 = row[3].split(',')
    triangles.append(numpy.array([[float(x1),float(y1)],[float(x2),float(y2)],[float(x3),float(y3)]]))
  return triangles

#############################################################################
# LOAD IN THE WORDS FROM A SPECIFIC SET FILE

def getWords(experiment, chain, generation, set_type):
  if set_type == "c":
    data = load(experiment, chain, generation, "d") + load(experiment, chain, generation, "s")
  else:
    data = load(experiment, chain, generation, set_type)
  return [data[x][0] for x in range(0,len(data))]

#############################################################################
# CONVERT MATRIX INTO VECTOR

def matrix2vector(matrix):
  vector = []
  for row in matrix:
    for cell in row:
      vector.append(cell)
  return vector

#############################################################################
# CALCULATE AVERAGE TIME SPENT ON EACH TEST ITEM

def timePerItem(experiment, chain, generation):
  set_d = load(experiment, chain, generation, "d")
  timestamp_1 = stringToTimeStamp(set_d[0][4])
  timestamp_50 = stringToTimeStamp(set_d[47][4])
  difference = timestamp_50 - timestamp_1
  time_per_item_set_d = difference.total_seconds() / 94.0
  return time_per_item_set_d

def stringToTimeStamp(string):
  tim = string.split(":")
  timestamp = timedelta(hours=int(tim[0]), minutes=int(tim[1]), seconds=int(tim[2]))
  return timestamp

#############################################################################
# GET THE OVERUSE COUNT FROM A PARTICIPANT'S LOG FILE (EXP 2 ONLY) I.E. THE
# NUMBER OF TIMES THEY WERE PROMPTED TO ENTER A NEW WORD

def overuseCount(chain, generation, subject):
  if subject == 'A' or subject == 'B':
    filename = 'logSub' + subject
  else:
    filename = 'log'
  data = load(2, chain, generation, filename)
  line = str(data[54])
  split1 = line.split("overuse count = ")
  split2 = split1[1].split("'")
  return int(split2[0])

#############################################################################
# GET STRUCTURE SCORES FOR ALL METRICS

def allMetrics(experiment, sims=1000):
  data = []
  for metric in ['dt','dtt','dtr','dts','dtrm','dtst','dtsr','dtsrm']:
    print "-------------\nMETRIC: " + metric + "\n-------------"
    data.append(allStructureScores(experiment, metric, sims))
  return data

#############################################################################
# GET STRUCTURE SCORES FOR ALL CHAINS IN AN EXPERIMENT

def allStructureScores(experiment, metric='dt', sims=1000):
  meanings = getTriangles(1, "A", 0, "s")
  meaning_distances = meaningDistances(meanings, metric)
  matrix = []
  for chain in chain_codes[experiment-1]:
    print "  Chain " + chain + "..."
    scores = []
    for generation in range(0, 11):
      if uniqueStrings(experiment, chain, generation)[1] > 1:
        scores.append(structureScore(experiment, chain, generation, metric, sims, meaning_distances))
      else:
        scores.append(None)
    matrix.append(scores)
  return matrix

#############################################################################
# CORRELATE THE STRING EDIT DISTANCES AND MEANING DISTANCES, THEN RUN THE
# DISTANCES THROUGH A MONTE CARLO SIMULATION. RETURN THE VERDICAL COEFFICIENT,
# THE MEAN AND STANDARD DEVIATION OF THE MONTE CARLO SAMPLE, AND THE Z-SCORE

def structureScore(experiment, chain, generation, metric='dt', simulations=1000, meaning_distances=None):
  strings = getWords(experiment, chain, generation, 's')
  string_distances = stringDistances(strings)
  if meaning_distances == None:
    meanings = getTriangles(experiment, chain, generation, 's')
    meaning_distances = meaningDistances(meanings, metric)
  z = MantelTest.MantelTest(string_distances, meaning_distances, simulations)[3]
  return z

# FOR EACH PAIR OF STRINGS, CALCULATE THE NORMALIZED LEVENSHTEIN DISTANCE
# BETWEEN THEM

def stringDistances(strings):
  distances = []
  for i in range(0,len(strings)):
    for j in range(i+1,len(strings)):
      ld = Levenshtein.distance(strings[i], strings[j])
      distances.append(ld/float(max(len(strings[i]), len(strings[j]))))
  return distances

# FOR EACH PAIR OF TRIANGLES, CALCULATE THE DISTANCE BETWEEN THEM

def meaningDistances(meanings, metric):
  distances = []
  if metric == "dt":
    for i in range(0,len(meanings)):
      for j in range(i+1,len(meanings)):
        distances.append(geometry.dT(meanings[i],meanings[j]))
  elif metric == "dtt":
    for i in range(0,len(meanings)):
      for j in range(i+1,len(meanings)):
        distances.append(geometry.dT_up_to_translation(meanings[i],meanings[j]))
  elif metric == "dtr":
    for i in range(0,len(meanings)):
      for j in range(i+1,len(meanings)):
        distances.append(geometry.dT_up_to_rotation(meanings[i],meanings[j]))
  elif metric == "dts":
    for i in range(0,len(meanings)):
      for j in range(i+1,len(meanings)):
        distances.append(geometry.dT_up_to_scale(meanings[i],meanings[j]))
  elif metric == "dtrm":
    for i in range(0,len(meanings)):
      for j in range(i+1,len(meanings)):
        distances.append(geometry.dT_up_to_rigid_motion(meanings[i],meanings[j]))
  elif metric == "dtst":
    for i in range(0,len(meanings)):
      for j in range(i+1,len(meanings)):
        distances.append(geometry.dT_up_to_scaled_translation(meanings[i],meanings[j]))
  elif metric == "dtsr":
    for i in range(0,len(meanings)):
      for j in range(i+1,len(meanings)):
        distances.append(geometry.dT_up_to_scaled_rotation(meanings[i],meanings[j]))
  elif metric == "dtsrm":
    for i in range(0,len(meanings)):
      for j in range(i+1,len(meanings)):
        distances.append(geometry.dT_up_to_scaled_rigid_motion(meanings[i],meanings[j]))
  else:
    print "Invalid metric"
    return False
  return distances

#############################################################################
# CALCULATE THE ENTROPY OF A LANGUAGE

def entropy(experiment, chain, generation):
  P = syllableProbabilities(experiment, chain, generation)
  return 0.0-sum([p*log2(p) for p in P.values()])

#############################################################################
# CALCULATE THE CONDITIONAL ENTROPY OF A LANGUAGE

def conditionalEntropy(experiment, chain, generation):
  X, Y, M = bisyllableProbabilities(experiment, chain, generation)
  N = float(len(X))
  return 0.0-sum([M[x][y]*log2(M[x][y]/(X[x]/N)) for x in X.keys() for y in Y.keys()])

#############################################################################
# GET SYLLABLE PROBABILITIES

def syllableProbabilities(experiment, chain, generation, start_stop=False):
  words = getWords(experiment, chain, generation, "d")
  segmented_words = segment(words, start_stop)
  syllables = {}
  for word in segmented_words:
    for syllable in word:
      if syllable in syllables.keys():
        syllables[syllable] += 1.0
      else:
        syllables[syllable] = 1.0
  N = float(sum(syllables.values()))
  for s in syllables.keys():
    syllables[s] = syllables[s]/N
  return syllables

def condEnt(experiment, chain, generation):
  syllables = syllableProbabilities(experiment, chain, generation, True)
  bisyllables = bisyllableProbabilities(experiment, chain, generation, True)
  H = 0.0
  for x in syllables.keys():
    p_x = syllables[x]
    total = 0.0
    for y in syllables.keys():
      if bisyllables.has_key(x+y) == True:
        p_xy = bisyllables[x+y]
        total += p_xy*log2(p_xy)
    H += (p_x * total)
  return -H

def bisyllableProbabilities(experiment, chain, generation, start_stop=True):
  words = getWords(experiment, chain, generation, "d")
  segmented_words = segment(words, start_stop)
  bisyllables = {}
  for word in segmented_words:
    for i in range(0,len(word)-1):
      bisyll = "".join(word[i:i+2])
      if bisyll in bisyllables.keys():
        bisyllables[bisyll] += 1.0
      else:
        bisyllables[bisyll] = 1.0
  N = float(sum(bisyllables.values()))
  for s in bisyllables.keys():
    bisyllables[s] = bisyllables[s]/N
  return bisyllables

#############################################################################
# SEGMENT WORDS INTO THEIR COMPONENT SYLLABLES

rules = [['zwac','zwAA'],['wac', 'wAA'],['ei', 'EY'],['oo','UW'],['or', 'AOr'],['ai', 'AY'],['ae', 'AY'],
       ['au', 'AW'],['oi', 'OY'],['o', 'OW'],['i', 'IY'],['a', 'AA'],
       ['e', 'EH'],['u', 'UW'],['ch', 'C'],['j', 'J'],['ck', 'k'],
       ['c', 'k'],['ng', 'N'],['sh', 'S'],['th', 'T']]

def segment(words, start_stop=False):
  segmented_words = []
  for i in range(0,len(words)):
    for rule in rules:
      words[i] = words[i].replace(rule[0], rule[1]+"|")
    if words[i][-1] == "|":
      words[i] = words[i][:-1]
    segmented_words.append(words[i].split("|"))
  for i in segmented_words:
    for j in range(0, len(i)):
      if len(i[j]) == 1:
        i[j-1] = i[j-1] + i[j]
        i.pop(j)
        j = j-1
    if start_stop == True:
      i.insert(0,"<")
      i.append(">")
  return segmented_words

#############################################################################
# WRITE OUT A MATRIX TO A FILE ON THE DESKTOP

def writeOut(matrix, filename='file'):
  data = ""
  for row in matrix:
    row = [str(x) for x in row]
    data = data + "\t".join(row) + "\n"
  data = data[0:-1]
  f = open('/Users/jon/Desktop/' + filename + '.txt', 'w')
  f.write(data)
  f.close()

#############################################################################
# READ IN A PREVIOUSLY SAVED DATA FILE TO A MATRIX

def readIn(filename):
  f = open(filename, 'r')
  data = f.read()
  f.close()
  lines = data.split("\n")
  matrix = []
  for line in lines:
    cells = line.split("\t")
    row = []
    for cell in cells:
      try:
        cell = float(cell)
      except:
        cell = None
      row.append(cell)
    matrix.append(row)
  return matrix

#############################################################################
# PLOT A SHAPE-SIZE SCATTER PLOT

def sizeShapePlot(experiment, chain, generation, use_clustering=False, clusters=5):
  triangles = getTriangles(experiment, chain, generation, 's')
  perimeters = [geometry.perimeter(T) for T in triangles]
  areas = [geometry.area(T) for T in triangles]
  words = getWords(experiment, chain, generation, 's')
  uniques = set(words)
  matrix = {}
  for word in uniques:
    dups = []
    for i in range(0, len(words)):
      if words[i] == word:
        dups.append(i)
    matrix[word] = dups
  colours = ["#2E578C","#5D9648","#E7A13D","black","#BC2D30","gray","purple","aqua"]
  i = 0
  fig, ax = plt.subplots(figsize=plt.figaspect(0.75))
  plt.rcParams['font.sans-serif']='Arial'
  if use_clustering == True:
    clustered_words = cluster(words, clusters)
    L=[]
    for c in clustered_words:
      P = [perimeters[x] for x in c]
      R = [areas[x] for x in c]
      L.append(set([words[x] for x in c]))
      ax.scatter(P, R, color=colours[i], s=40, marker="o")
      i += 1
    clust_labels = []
    print L
    for x in range(1,clusters+1):
      if len(L[x-1]) > 1:
        clust_labels.append("cluster "+str(x))
      else:
        clust_labels.append(str(L[x-1])[6:-3])
    l = plt.legend(clust_labels, loc=2, scatterpoints=1)
  else:
    for word in matrix.keys():
      P = [perimeters[x] for x in matrix[word]]
      R = [areas[x] for x in matrix[word]]
      ax.scatter(P, R, color=colours[i], s=40, marker="o")
      i += 1
    l = plt.legend(matrix.keys(), loc=2, scatterpoints=1)
  l.draw_frame(False)
  ax.plot(range(100,1401), [(p**2)/(12*sqrt(3)) for p in range(100,1401)], color='k', linestyle='-', linewidth=2.0)
  plt.xticks(fontsize=14)
  plt.yticks(fontsize=14)
  plt.xlabel("Perimeter", fontsize=22)
  plt.ylabel("Area (log scale)", fontsize=22)
  plt.xlim(100,1400)
  plt.ylim(100,100000)
  plt.semilogy()
  #plt.savefig(chain+str(generation)+".pdf", transparent=True)
  plt.show()

#############################################################################
# CLUSTER WORDS AND RETURN

def cluster(words, clusters):
  linkage_matrix = clusterWords(words)
  clustered_words = getClusters(linkage_matrix, clusters, len(words))
  return clustered_words

#############################################################################
# PERFORM AGGLOMERATIVE HIERARCHICAL CLUSTERING AND RETURNS LINKAGE MATRIX

def clusterWords(words):
  distance_matrix = numpy.array([])
  for i in range(0, len(words)):
    for j in range(i + 1, len(words)):
      ld = Levenshtein.distance(words[i], words[j])
      nld = ld/float(max(len(words[i]), len(words[j])))
      distance_matrix = numpy.append(distance_matrix, nld)
  distSquareMatrix = scipy.spatial.distance.squareform(distance_matrix)
  linkage_matrix = scipy.cluster.hierarchy.average(distSquareMatrix)
  return linkage_matrix

#############################################################################
# GET BUILDING BLOCKS GIVEN A LINKAGE MATRIX AND SPECIFIC NUMBER OF BLOCKS

def getClusters(linkage_matrix, clusters, n):
  blocks = [[x] for x in range(0,n)]
  for i in linkage_matrix:
    if len([value for value in blocks if value != None]) == clusters:
      break
    else:
      merged_block = blocks[int(i[0])] + blocks[int(i[1])]
      blocks.append(merged_block)
      blocks[int(i[0])] = None
      blocks[int(i[1])] = None
  return [value for value in blocks if value != None]

def intergenCorr(experiment):
  ln_data = readIn("/Users/jon/Desktop/Experiment " +str(experiment) + " data/ln.txt")
  st_data = readIn("/Users/jon/Desktop/Experiment " +str(experiment) + " data/st.txt")
  y = matrix2vector(ln_data)
  x = matrix2vector(st_data)

  r, p = stats.pearsonr(x,y)
  n = len(x)
  print r, n, p
  m, b = polyfit(x, y, 1)
  ln = [(m*i)+b for i in range(-4,11)]

  fig, ax = plt.subplots(figsize=plt.figaspect(0.625))
  ax.scatter(x, y, marker="x", color='k', s=60)
  ax.plot(range(-4,11), ln, color="k", linewidth=2.0)
  plt.xlim(-4,10)
  plt.gcf().subplots_adjust(bottom=0.12)
  plt.xlabel("Structure score ($d_{T_{rm}}$) for generation $i-1$", fontsize=22)
  plt.ylim(-2,8)
  plt.ylabel("Learnability score for generation $i$", fontsize=22)
  plt.xticks(fontsize=14)
  plt.yticks(fontsize=14)
  plt.show()

def triangleOverlayGraphic(experiment, chain, generation, word, col, spot_based=True):
  colours = ["#2E578C","#5D9648","#E7A13D","black","#BC2D30","#7D807F","#6F3D79"]
  washed_colours = ["#9AB4D0", "#AED4A7", "#F8D796", "#7F7F7F", "#EA949A", "#C6C8C8", "#C4A2C7"]
  colour = colours[col]
  w_colour = washed_colours[col]
  words = getWords(experiment, chain, generation, "s")
  T = getTriangles(experiment, chain, generation, "s")
  svg = ""
  T_new = []
  for i in range(0, len(words)):
    if words[i] in word:
      if words[i] == "mappakiki":
        w_colour = "#7F7F7F"
      else:
        w_colour = "#EA949A"
      svg = svg + "  <g id='word "+str(i)+"'>\n    <polygon points='"+str(T[i][0][0])+","+str(T[i][0][1])+" "+str(T[i][1][0])+","+str(T[i][1][1])+" "+str(T[i][2][0])+","+str(T[i][2][1])+"' style='fill:none;stroke:"+w_colour+";stroke-width:3;stroke-linejoin:miter;'/>\n    <circle cx='"+str(T[i][0][0])+"' cy='"+str(T[i][0][1])+"' r='8' style='stroke:"+w_colour+";fill:"+w_colour+";'/>\n  </g>\n"

      t = geometry.translate(T[i], numpy.array([[250.,250.],[250.,250.],[250.,250.]]))

      if spot_based == True:
        t = geometry.rotate(t)
      else:
        a, b, c = geometry.angle(t,1), geometry.angle(t,2), geometry.angle(t,3)
        angles = {'a':a, 'b':b, 'c':c}
        min_ang = min(angles, key=angles.get)
        if min_ang == 'a':
          t = numpy.array([[t[0][0], t[0][1]], [t[1][0], t[1][1]], [t[2][0], t[2][1]]])
        elif min_ang == 'b':
          t = numpy.array([[t[1][0], t[1][1]], [t[2][0], t[2][1]], [t[0][0], t[0][1]]])
        elif min_ang == 'c':
          t = numpy.array([[t[2][0], t[2][1]], [t[0][0], t[0][1]], [t[1][0], t[1][1]]])
        t = geometry.rotate(t)

      if t[1][0] > t[2][0]:
        t = numpy.array([t[0],t[2],t[1]])
      T_new.append(t)
  N = len(T_new)
  x1 = sum([T_new[x][0][0] for x in range(0,N)])/float(N)
  y1 = sum([T_new[x][0][1] for x in range(0,N)])/float(N)
  x2 = sum([T_new[x][1][0] for x in range(0,N)])/float(N)
  y2 = sum([T_new[x][1][1] for x in range(0,N)])/float(N)
  x3 = sum([T_new[x][2][0] for x in range(0,N)])/float(N)
  y3 = sum([T_new[x][2][1] for x in range(0,N)])/float(N)
  P = numpy.array([[x1,y1],[x2,y2],[x3,y3]])
  svg = svg + "\n  <g id='prototype'>\n    <polygon points='"+str(P[0][0])+","+str(P[0][1])+" "+str(P[1][0])+","+str(P[1][1])+" "+str(P[2][0])+","+str(P[2][1])+"' style='fill:"+colour+";fill-opacity:0.9;stroke:"+colour+";stroke-width:3;stroke-join:miter'/>\n  </g>\n"
  writeOutSVG(svg, word[0])
  return

def writeOutSVG(svg, name):
  data = "<svg xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:svg='http://www.w3.org/2000/svg' xmlns='http://www.w3.org/2000/svg' version='1.1' width='500' height='500'>\n"+svg+"</svg>"
  f = open('/Users/jon/Desktop/' + name + '.svg', 'w')
  f.write(data)
  f.close()

def drawTriangles(triangles, colours, filename):
  svg = ""
  for i in range(0,len(triangles)):
    c = geometry.centroid(triangles[i])
    svg += '''
<g id='triangle %s'>
<polygon points='%s,%s %s,%s %s,%s' style='fill:none;stroke:%s;stroke-width:3;stroke-linejoin:miter;'/>
<circle cx='%s' cy='%s' r='8' style='stroke:%s;fill:%s;'/>
</g>
''' % (i, triangles[i][0][0], triangles[i][0][1], triangles[i][1][0], triangles[i][1][1], triangles[i][2][0], triangles[i][2][1], colours[i], triangles[i][0][0], triangles[i][0][1], colours[i], colours[i])
  writeOutSVG(svg, filename)
  return

def wordMemory(experiment, chain, generation):
  words_a = set(getWords(experiment, chain, generation, 'c'))
  words_b = set(getWords(experiment, chain, generation-1, 'd'))
  n = float(max(len(words_a),len(words_b)))
  return len(words_a.intersection(words_b))/n

def soundSymbolism(experiment, chain, generation):
  words = getWords(experiment, chain, generation, 'c')
  segmented_words = segment(words, False)
  T = getTriangles(experiment, chain, generation, 'c')
  sounds = {'b':[], 'C':[], 'd':[], 'D':[], 'f':[], 'g':[], 'h':[], 'J':[], 'k':[], 'l':[], 'm':[], 'n':[], 'N':[], 'p':[], 'r':[], 's':[], 'S':[], 't':[], 'T':[], 'v':[], 'w':[], 'y':[], 'z':[], 'Z':[], 'AE':[], 'EY':[], 'AO':[], 'AX':[], 'IY':[], 'EH':[], 'IH':[], 'AY':[], 'AA':[], 'UW':[], 'UH':[], 'UX':[], 'OW':[], 'AW':[], 'OI':[]}
  for i in range(0,48):
    area_ratio = pointedness(T[i])
    theta = min([geometry.angle(T[i],1), geometry.angle(T[i],2), geometry.angle(T[i],3)])
    phon = "".join(segmented_words[i])
    for sound in sounds.keys():
      if phon.count(sound) > 0:
        sounds[sound].append(area_ratio)
    sound_counts = {}
    for sound in sounds.keys():
      if len(sounds[sound]) > 0:
        sound_counts[sound] = sum(sounds[sound])/float(len(sounds[sound]))
  return sound_counts

def pointedness(T):
  perimeter = geometry.perimeter(T)
  area = geometry.area(T)
  expected_area = (perimeter**2)/20.784609691
  return log(expected_area/area)

def allSoundSymbolism(experiment,start_gen, end_gen):
  import pointedness
  ss  =[[soundSymbolism(experiment,x,y) for y in range(start_gen,end_gen)] for x in chain_codes[experiment-1]]
  ss_v = matrix2vector(ss)
  sounds = {'AA':[],'IY':[],'OW':[], 'UW':[], 'b':[], 'C':[], 'd':[], 'D':[], 'f':[], 'g':[], 'h':[], 'J':[], 'k':[], 'l':[], 'm':[], 'n':[], 'N':[], 'p':[], 'r':[], 's':[], 'S':[], 't':[], 'T':[], 'v':[], 'w':[], 'y':[], 'z':[], 'Z':[], 'AE':[], 'EY':[], 'AO':[], 'AX':[], 'EH':[], 'IH':[], 'AY':[], 'UH':[], 'UX':[], 'AW':[], 'OI':[]}
  for i in ss_v:
    for j in i.keys():
      sounds[j].append(i[j])
  matrix = []
  ipaLabels = ipaLabels = {'AA':u"ɑː",'IY':u"iː",'OW':u"əʊ", 'UW':u"uː", 'b':u"b", 'C':u"tʃ", 'd':u"d", 'D':u"ð", 'f':u"f", 'g':u"g", 'h':u"h", 'J':u"dʒ", 'k':u"k", 'l':u"l", 'm':u"m", 'n':u"n", 'N':u"ŋ", 'p':u"p", 'r':u"r", 's':u"s", 'S':u"ʃ", 't':u"t", 'T':u"θ", 'v':u"v", 'w':u"w", 'y':u"j", 'z':u"z", 'Z':u"ʒ", 'AE':u"a", 'EY':u"eɪ", 'AO':u"ɔː", 'AX':u"ə", 'EH':u"ɛ", 'IH':u"ɪ", 'AY':u"ʌɪ", 'UH':u"ə", 'UX':u"ʌ", 'AW':u"aʊ", 'OI':u"ɔɪ"}
  expected = pointedness.run(10000)
  for i in sounds.keys():
    if len(sounds[i]) > 20:
      mw = scipy.stats.mannwhitneyu(expected, sounds[i])
      matrix.append([ipaLabels[i], mean(sounds[i]), std(sounds[i]), (std(sounds[i])/sqrt(len(sounds[i])))*1.959964, mw[0], mw[1]*2])
  return matrix

def plotSoundSymbolism(matrix, y_label="Pointedness", miny=0.0, maxy=2, baseline=False):
  fig, ax = plt.subplots(figsize=plt.figaspect(0.625))
  n = len(matrix)
  if baseline == True:
    ax.plot(range(-1,n+1), [0.85]*(n+2), color='gray', linestyle=':')
  xvals = range(0,n)
  means = [row[1] for row in matrix]
  errors = [row[3] for row in matrix]
  pvals = [row[5] for row in matrix]
  (_, caps, _) = ax.errorbar(xvals, means, fmt="o", yerr=errors, color='k', linestyle="", linewidth=2.0, capsize=5.0, elinewidth=1.5)
  for cap in caps:
    cap.set_markeredgewidth(2)
  for i in xvals:
    sig = ""
    if pvals[i] <= 0.001:
      sig = "***"
    elif pvals[i] <= 0.01:
      sig = "**"
    elif pvals[i] <= 0.05:
      sig = "*"
    ax.annotate(sig, xy=(i,means[i]+errors[i]+0.05), zorder=10, color="red")
  labels = [row[0] for row in matrix]
  plt.xticks(xvals, labels, fontsize=14)
  plt.yticks(fontsize=14)
  plt.xlim(-0.5, n-0.5)
  plt.ylim(miny, maxy)
  plt.xlabel("Sounds", fontsize=22)
  plt.ylabel(y_label, fontsize=22)
  plt.show()
