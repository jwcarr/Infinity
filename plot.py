import math
from string import ascii_uppercase
import matplotlib.pyplot as plt
import numpy as np


label_font_size = 10
axis_font_size = 8
legend_font_size = 10
line_thickness = 1.0
colours_for_experiment = [['#01AAE9', '#1B346C', '#F44B1A', '#E5C39E'],
                          ['#F6C83C', '#4C5B28', '#DB4472', '#B77F60'],
                          ['#CBB345', '#609F80', '#4B574D', '#AF420A']]


def plot(matrix, mean_line=False, starting_gen=1, miny=0.0, maxy=1.0, y_label="Score", text=False, conf=False, col=1, text_pos='bottom', save=False, matrix_2=False, starting_gen_2=1, miny_2=0.0, maxy_2=1.0, y_label_2="Score", text_2=False, conf_2=False, col_2=1):
  
  # Initialize figure
  plt.figure(1)

  # Replace NaN with None if present in the matrix
  matrix = RemoveNaN(matrix)

  if matrix_2 != False:
    matrix_2 = RemoveNaN(matrix_2)
    if mean_line == True:
      plt.subplots(figsize=(5.5, 2.5))
      ax1 = plt.subplot2grid((6,2), (0,0), rowspan=6)
    else:
      plt.subplots(figsize=(5.5, 3.0))
      ax1 = plt.subplot2grid((6,2), (0,0), rowspan=5)
  else:
    if mean_line == True:
      plt.subplots(figsize=(5.5, 2.5))
      ax1 = plt.subplot2grid((6,1), (0,0), rowspan=6)
    else:
      plt.subplots(figsize=(5.5, 3.0))
      ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5)

  n = len(matrix[0])
  colours = colours_for_experiment[col-1]
  xvals = range(starting_gen, n+starting_gen)
  if conf == True:
    plt.plot(range(-1,n+1), [1.959964] * (n+2), color='gray', linestyle=':', linewidth=0.5)
    if miny < -2.0:
      plt.plot(range(-1,n+1), [-1.959964] * (n+2), color='gray', linestyle=':', linewidth=0.5)
  elif type(conf) == int:
    plt.plot(range(-1,n+1), [conf] * (n+2), color='gray', linestyle=':', linewidth=0.5)

  if mean_line == True:
    x_vals = range(starting_gen, len(matrix[0])+starting_gen)
    means, errors = MeanWithErrors(matrix)
    _, caps, _ = ax1.errorbar(x_vals, means, yerr=errors, color='k', marker='o', markersize=3.0, linestyle="-", linewidth=line_thickness, capsize=1, elinewidth=0.5)
    for cap in caps:
      cap.set_markeredgewidth(0.5)
    plt.xlim(starting_gen-0.5, n+starting_gen-0.5)
  else:
    for i in range(0,len(matrix)):
      x_vals = range(starting_gen, len(matrix[i])+starting_gen)
      y_vals = [item for item in matrix[i]]
      plt.plot(x_vals, y_vals, color=colours[i], linewidth=line_thickness, label='Chain ' + ascii_uppercase[((col-1)*4)+i:((col-1)*4)+i+1])
    plt.xlim(starting_gen, n+starting_gen-1)

  labels = range(starting_gen, starting_gen+n)
  plt.ylim(miny, maxy)
  plt.xticks(xvals, labels, fontsize=axis_font_size)
  plt.yticks(fontsize=axis_font_size)
  plt.xlabel("Generation number", fontsize=label_font_size)
  plt.ylabel(y_label, fontsize=label_font_size)
  plt.tick_params(axis='x', which='both', bottom='off', top='off')
  if text != False:
    if text_pos == 'bottom':
      text_y = miny + ((maxy+abs(miny))/15.)
    else:
      text_y = maxy - (((maxy+abs(miny))/15.)*1.75)
    if mean_line == True:
      plt.text(0.0, text_y, text, {'fontsize':8})
    else:
      plt.text(0.5, text_y, text, {'fontsize':8})

  if matrix_2 != False:
    if mean_line == True:
      ax2 = plt.subplot2grid((6,2), (0,1), rowspan=6)
    else:
      ax2 = plt.subplot2grid((6,2), (0,1), rowspan=5)
    n = len(matrix_2[0])
    colours = colours_for_experiment[col_2-1]
    xvals = range(starting_gen_2, n+starting_gen_2)
    if conf_2 == True:
      plt.plot(range(0,n+1), [1.959964] * (n+1), color='gray', linestyle=':')
      if miny_2 < -2.0:
        plt.plot(range(0,n+1), [-1.959964] * (n+1), color='gray', linestyle=':')
    elif type(conf_2) == int:
      plt.plot(range(0,n+1), [conf_2] * (n+1), color='gray', linestyle=':')

    if mean_line == True:
      x_vals = range(starting_gen_2, len(matrix_2[0])+starting_gen_2)
      means, errors = MeanWithErrors(matrix_2)
      _, caps, _ = ax2.errorbar(x_vals, means, yerr=errors, marker='o', markersize=3.0, color='k', linestyle="-", linewidth=line_thickness, capsize=1, elinewidth=0.5)
      for cap in caps:
        cap.set_markeredgewidth(0.5)
      plt.xlim(starting_gen_2-0.5, n+starting_gen_2-0.5)
    else:
      for i in range(0,len(matrix_2)):
        x_vals = range(starting_gen_2, len(matrix_2[i])+starting_gen_2)
        y_vals = [item for item in matrix_2[i]]
        plt.plot(x_vals, y_vals, color=colours[i], linewidth=line_thickness)
      plt.xlim(starting_gen_2, n+starting_gen_2-1)

    labels = range(starting_gen_2, starting_gen_2+n)
    plt.ylim(miny_2, maxy_2)
    plt.xticks(xvals, labels, fontsize=axis_font_size)
    plt.yticks(fontsize=axis_font_size)
    plt.xlabel("Generation number", fontsize=label_font_size)
    if y_label_2 != False:
      plt.ylabel(y_label_2, fontsize=label_font_size)
    if (miny == miny_2) and (maxy == maxy_2):
      ax2.set_yticklabels([])
    plt.tick_params(axis='x', which='both', bottom='off', top='off')
    if text_2 != False:
      if text_pos == 'bottom':
        text_y = miny + ((maxy_2+abs(miny_2))/15.)
      else:
        text_y = maxy_2 - (((maxy_2+abs(miny_2))/15.)*1.75)
      if mean_line == True:
        plt.text(0.0, text_y, text_2, {'fontsize':8})
      else:
        plt.text(0.5, text_y, text_2, {'fontsize':8})

  if mean_line == False:
    if matrix_2 != False:
      ax3 = plt.subplot2grid((6,2), (5,0), colspan=2)
    else:
      ax3 = plt.subplot2grid((6,1), (5,0))
    plt.axis('off')
    handles, labels = ax1.get_legend_handles_labels()
    ax3.legend(handles, labels, loc='upper center', frameon=False, prop={'size':legend_font_size}, ncol=4)

  plt.tight_layout(pad=0.2, w_pad=1.0, h_pad=0.00)

  plt.savefig(save)
  plt.clf()


def all(dataset, starting_gen=False, miny=False, maxy=False, y_label=False, text=False, conf=False, colour_set=False, text_pos=False, save_location=False, save_name=False, dataset2=False, starting_gen2=False, miny2=False, maxy2=False, y_label2=False, text2=False, conf2=False, colour_set2=False):
  
  if starting_gen == False:
    if len(dataset[0]) == 10:
      starting_gen = 1
    else:
      starting_gen = 0
  if miny == False:
    miny = 0
  if maxy == False:
    maxy = 1
  if y_label == False:
    y_label = "Score"
  if text != False and text_pos == False:
    text_pos = 'bottom'
  if colour_set == False:
    colour_set = 0
  if save_location == False:
    save_location = '/Users/jon/Desktop/'
  if save_name == False:
    save_name = 'plot.eps'

  if dataset2 != False:
    if starting_gen2 == False:
      if len(dataset2[0]) == 10:
        starting_gen2 = 1
      else:
        starting_gen2 = 0
    if miny2 == False:
      miny2 = miny
    if maxy2 == False:
      maxy2 = maxy
    if text2 != False and text_pos2 == False:
      text_pos2 = test_pos
    if conf2 == False:
      conf2 = conf
    if colour_set2 == False:
      colour_set2 = colour_set

  plot(dataset, False, starting_gen, miny, maxy, y_label, text, conf, colour_set, text_pos, save_location+save_name, dataset2, starting_gen2, miny2, maxy2, y_label2, text2, conf2, colour_set2)



def mean(dataset, starting_gen=False, miny=False, maxy=False, y_label=False, text=False, conf=False, colour_set=False, text_pos=False, save_location=False, save_name=False, dataset2=False, starting_gen2=False, miny2=False, maxy2=False, y_label2=False, text2=False, conf2=False, colour_set2=False):
  
  if starting_gen == False:
    if len(dataset[0]) == 10:
      starting_gen = 1
    else:
      starting_gen = 0
  if miny == False:
    miny = 0
  if maxy == False:
    maxy = 1
  if y_label == False:
    y_label = "Score"
  if text != False and text_pos == False:
    text_pos = 'bottom'
  if colour_set == False:
    colour_set = 0
  if save_location == False:
    save_location = '/Users/jon/Desktop/'
  if save_name == False:
    save_name = 'plot.eps'

  if dataset2 != False:
    if starting_gen2 == False:
      if len(dataset2[0]) == 10:
        starting_gen2 = 1
      else:
        starting_gen2 = 0
    if miny2 == False:
      miny2 = miny
    if maxy2 == False:
      maxy2 = maxy
    if text2 != False and text_pos2 == False:
      text_pos2 = test_pos
    if conf2 == False:
      conf2 = conf
    if colour_set2 == False:
      colour_set2 = colour_set

  plot(dataset, True, starting_gen, miny, maxy, y_label, text, conf, colour_set, text_pos, save_location+save_name, dataset2, starting_gen2, miny2, maxy2, y_label2, text2, conf2, colour_set2)


def MeanWithErrors(matrix):
  means = []
  errors = []
  for i in range(0,len(matrix[0])):
    column = [row[i] for row in matrix if row[i] != None]
    means.append(np.mean(column))
    errors.append((np.std(column) / np.sqrt(len(column))) * 1.959964)
  return means, errors


def RemoveNaN(matrix):
  new_matrix = []
  for row in matrix:
    new_row = []
    for cell in row:
      if cell != None:
        if math.isnan(cell) == True:
          new_row.append(None)
        elif math.isinf(cell) == True:
          new_row.append(None)
        else:
          new_row.append(cell)
    new_matrix.append(new_row)
  return new_matrix