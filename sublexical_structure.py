from itertools import permutations
from math import factorial
from scipy.spatial.distance import squareform
import numpy as np

def test(strings, meaning_distances, perms):

  # Determine category labels and the edit-distances between them
  category_labels = list(set(strings))
  label_distances = squareform(pairwise_string_distances(category_labels))

  # Compute meaning distance residuals
  meaning_residuals = residualize(meaning_distances)

  # Number of strings, number of categories, and number of category permutations
  m = len(strings)
  n = len(category_labels)
  p = factorial(n)

  # Deterministic test - measure every possible category-meaning mapping
  if p <= perms:

    # Create an empty array to store the covariences
    covariences = np.zeros(p, dtype=float)

    # Enumerate all permutations of category label orders
    for i, order in enumerate(permutations(range(n))):

      # Rearrange the category labels into a new order
      permuted_category_labels = [category_labels[j] for j in order]

      # Compile the string distances from the pre-computed label_distances matrix
      # This is faster than recomputing all the Levenshtein edit-distances from scratch
      string_distances = []
      for j in range(0, m):
        idx1 = permuted_category_labels.index(strings[j])
        for k in range(j+1, m):
          idx2 = permuted_category_labels.index(strings[k])
          string_distances.append(label_distances[idx1, idx2])

      # Residualize the string distances
      string_residuals = residualize(string_distances)

      # Store the covarience between meaning distances and string distances
      covariences[i] = (meaning_residuals * string_residuals).sum()

  # Stochasitc test - randomly sample the space of category-meaning mappings
  else:

    # Create an empty array to store the covariences
    covariences = np.zeros(perms, dtype=float)

    # Compute the veridical covarience and store it in first position
    string_residuals = residualize(pairwise_string_distances(strings))
    covariences[0] = (meaning_residuals * string_residuals).sum()

    # For each permutation...
    for i in range(1, perms):

      # Shuffle the order of category labels
      np.random.shuffle(category_labels)

      # Compile the string distances from the pre-computed label_distances matrix
      # This is faster than recomputing all the Levenshtein edit-distances from scratch
      string_distances = []
      for j in range(0, m):
        idx1 = category_labels.index(strings[j])
        for k in range(j+1, m):
          idx2 = category_labels.index(strings[k])
          string_distances.append(label_distances[idx1, idx2])

      # Residualize the string distances
      string_residuals = residualize(string_distances)

      # Store the covarience between meaning distances and string distances
      covariences[i] = (meaning_residuals * string_residuals).sum()

  # Return standard score (z-score)
  return (covariences[0] - covariences.mean()) / covariences.std()

# Return the residuals of an array
def residualize(distances):
  distances = np.asarray(distances, dtype=float)
  return distances - distances.mean()

# Take a list of strings and compute the pairwise edit-distances
def pairwise_string_distances(strings):
  distances = []
  for i in range(0, len(strings)):
    for j in range(i+1, len(strings)):
      distances.append(norm_Levenshtein_distance(strings[i], strings[j]))
  return np.array(distances, dtype=float)

# Calculate the normalized Levenshtein distance between two strings
def norm_Levenshtein_distance(string1, string2):
  if len(string1) > len(string2):
    string1, string2 = string2, string1
  distances = range(len(string1) + 1)
  for index2, char2 in enumerate(string2):
    newDistances = [index2 + 1]
    for index1, char1 in enumerate(string1):
      if char1 == char2:
        newDistances.append(distances[index1])
      else:
        newDistances.append(1 + min((distances[index1], distances[index1+1], newDistances[-1])))
    distances = newDistances
  return float(distances[-1]) / max(len(string1), len(string2))
