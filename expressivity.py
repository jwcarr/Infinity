import basics
import plot as plt

def experiment_results(experiment, set_type='s'):
  results = []
  for chain in basics.chain_codes[experiment-1]:
    results.append(chain_results(chain, set_type, experiment))
  return results

def chain_results(chain, set_type='s', experiment=False):
  if type(experiment) == bool and experiment == False:
    experiment = basics.determine_experiment_number(chain)
  results = []
  for generation in range(0, 11):
    results.append(generation_results(chain, generation, set_type, experiment))
  return results

def generation_results(chain, generation, set_type='s', experiment=False):
  if type(experiment) == bool and experiment == False:
    experiment = basics.determine_experiment_number(chain)
  return basics.uniqueStrings(experiment, chain, generation, set_type)

def plot(left_data, right_data, experiment, save_location=False):
  if experiment == 2:
    conf = 16
  else:
    conf = False
  plt.chains(left_data, dataset2=right_data, miny=0, maxy=50, y_label='Number of unique strings', text='(A)', text2='(B)', text_pos='bottom', experiment=experiment, conf=conf, save_location=save_location, save_name='E%i_expressivity.pdf'%experiment)