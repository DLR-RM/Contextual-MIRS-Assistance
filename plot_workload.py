import numpy as np
import collections
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
import math
import collections
import os

font = {'family' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 10}

matplotlib.rc('font', **font)
plt.rcParams["figure.figsize"] = (4,2.5)


CONTROL = False



color_list_inkscape = [ (0,125,197,255), (64,152,211,255), (148,188,228,255), (52,86,31,255),(82,116,61,255),(112,146,91,255),(148,171,130,255), (189,201,176,255)]

color_list = []
for tuple in color_list_inkscape:
    color_list.append(np.divide(np.asarray(tuple),255.))


if CONTROL:
    VP_list = [8,  9, 10]
else:
    VP_list = [1,  3,  5]

### results
task1 = collections.OrderedDict([("with1",[5,4,8,11,5,4,2,11,3,12]),
                                 ("with2", [8,4,8,11,4,6,2,11,3,14]),
                                 ("with3", [5,3,6,10,5,4,2,10,3,12]),
                                 ("without1", [11,5,13,12,10,6,2,12,4,13]),
                                 ("without2", [7,4,7,12,5,3,1,10,3,13]),
                                 ])
task2 = collections.OrderedDict([("with1",[4,4,4,8,1,3,4,11,12,15]),
                                 ("with2", [7,5,6,10,2,4,2,11,11,16]),
                                 ("with3", [6,3,7,11,2,3,3,12,10,16]),
                                 ("without1", [10,7,12,15,4,3,5,10,11,16]),
                                 ("without2", [10,4,9,13,4,2,4,10,10,15]),
                                 ])

fig_hist_work = None
task_idx = 0
task_list =  [collections.OrderedDict(), collections.OrderedDict()]

task_count = 0
for task in [task1,task2]:
    for trial_name in task:
        task_list[task_count][trial_name] = [task[trial_name][i-1] for i in VP_list]
    task_count += 1



task_idx_list = [0,2]
for task in task_list:
    if CONTROL:
        color_count = 3
    else:
        color_count = 0
    without_count = 0
    count = 0

    for trial, workload in task.iteritems():
        mean = np.mean(workload)
        error = np.std(workload)
        if fig_hist_work is None:
            fig_hist_work = plt.figure()
            ax_work = fig_hist_work.add_subplot(111)

        if 'without' in trial:
            offset = [-0.2, 0.2]
            offset_curr = offset[without_count]
            without_count +=1
            label = 'without ' +str(without_count)
        else:
            offset = [ -0.1, 0.0, 0.1]
            offset_curr = offset[count]
            label = "with " +str(count)
            count +=1

        ax_work.bar(task_idx_list[task_idx] + offset_curr,mean,yerr = error, width = 0.1, label = label, color = color_list[color_count],ecolor='black')
        ax_work.set_ylim(0, 20)
        color_count +=1

    task_idx +=1

ax_work.set_xticks(range(3))
ax_work.set_xticklabels(['benchmark one', '', 'benchmark two'])


save_fig_path = os.getcwd()+'/plots/'
#plt.legend()
if CONTROL:
    fig_hist_work.savefig(save_fig_path + 'control_workload.pdf', bbox_inches='tight')
else:
    fig_hist_work.savefig(save_fig_path + 'workload.pdf', bbox_inches='tight')
