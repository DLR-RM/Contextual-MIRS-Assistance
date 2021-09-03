import copy
import pickle
import pandas as pd
import matplotlib
#matplotlib.use('gtk3agg')
import numpy as np
matplotlib.use('pdf')
import matplotlib.pyplot as plt
import os,time


#data = pickle.load(file)
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import math
import collections

font = {'family' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 10}

matplotlib.rc('font', **font)

### DIN A4 page: 8.27 times 11.69 inches

plt.rcParams["figure.figsize"] = (4,2.5)

PLOT_SPLINE = True
PLOT_PER_VP = False
CONTROL = True
PLOT_FORCES = True

USE_PREDEFINED_MAX_WRENCH = True





############## paper####################

userstudy_folder_path = 'data/'

if CONTROL:
    additional_part = 'control_'
else:
    additional_part = ''


if PLOT_SPLINE:
        save_fig_path = 'plots/'  + additional_part+'spline_'
else:
    save_fig_path = 'plots/'+ additional_part

if CONTROL:
    VP_list = ['VP8',  'VP9', 'VP10']
else:
    VP_list = ['VP1',  'VP3',  'VP5']


if USE_PREDEFINED_MAX_WRENCH:
    max_wrench = {'pick':[19295, 1609],'place':[19295, 1609], 'PF': [73759, 0] }




file_names = ['fixture_forces_info1','fixture_forces_info2','sct_data','gripper_pos', 'calculated_spline_forces_for_gripper_pos']






def fill_folder_list(names_list,spline = True):
    empty_list = []
    for name in names_list:
        if 'spline' in name and spline:
            empty_list.append(name)
        elif 'spline' not in name and not spline:
            empty_list.append(name)
    return empty_list




def accumulate_forces_per_state(forces_list,states_list, forces_list_spline = []):
    forces_per_states = {}
    idx = 0
    use_both = False

    for state in states_list:
        #print forces_list[idx]
        if 'transition' in state or 'grasped' in state and len(forces_list_spline)>1 and PLOT_SPLINE:
            forces_list_to_use = forces_list_spline
        else:
            forces_list_to_use = forces_list
        if state in forces_per_states.keys() and idx < len(forces_list_to_use):
            forces_per_states[state]=np.add(forces_per_states[state],forces_list_to_use[idx])

        elif  idx < len(forces_list_to_use):
            forces_per_states[state]=copy.deepcopy(forces_list_to_use[idx])

        idx += 1
    return forces_per_states


def norm_forces(forces_list):
    normed_forces = []
    count = 0
    for forces in forces_list:
        normed_forces.append([math.sqrt(sum(forces[0:3]*forces[0:3])), math.sqrt(sum(forces[3:]*forces[3:]))])
        count +=1

    return normed_forces

def add_task_wise(forces_dict):
    task_dict = {}
    forces_shape = 0
    iterable = False
    for task, states in task_states.items():
        for s in states:
            if task in task_dict.keys() and s in forces_dict.keys():
                #print "entries "
                #print task_dict[task]
                #print forces_dict[s]
                task_dict[task]=np.add(task_dict[task],forces_dict[s])

            elif s in forces_dict.keys():
                task_dict[task]=copy.deepcopy(forces_dict[s])
                if  isinstance(forces_dict[s], list):
                    forces_shape = (len(forces_dict[s]))
                    iterable = True
                elif isinstance(forces_dict[s], np.ndarray):
                    forces_shape = forces_dict[s].shape
                    iterable = True



    for task in task_states.keys():
        if task not in task_dict.keys():
            if iterable:
                task_dict[task]=np.zeros(forces_shape)
            else:
                task_dict[task] = forces_shape
    #print task_dict


    return task_dict


def get_duration_per_state(time, states_list):
    idx = 0
    start_end_per_state = {}
    time_float = []
    for t in time:
        time_float.append(float(t))
    time_to_use = np.asarray(time_float) - time_float[0]
    for state in states_list:
        if state not in start_end_per_state.keys():
            start_end_per_state[state] = []
            start_end_per_state[state].append([time_to_use[idx]])
        elif state_before != state:
            start_end_per_state[state].append([time_to_use[idx]])
        elif len(start_end_per_state[state][-1]) ==1:
            start_end_per_state[state][-1].append(time_to_use[idx])
        elif len(start_end_per_state[state][-1]) ==2:
            start_end_per_state[state][-1][1] = time_to_use[idx]
        state_before = copy.deepcopy(state)
        idx += 1
    #print "start_end_per_state " +str(start_end_per_state)
    duration_per_state = {}
    for state, times_list in start_end_per_state.items():
        sum  = 0
        for entry in times_list:
            sum += entry[1]-entry[0]
        duration_per_state[state] = sum
    #print "duration per state " +str(duration_per_state)
    #print "added task wise " +str(add_task_wise(duration_per_state))
    return add_task_wise(duration_per_state)





all_data = {}

acc_forces_per_task = collections.OrderedDict()
durations_per_task = collections.OrderedDict()
options_count = collections.OrderedDict()
options_count['with']= range(1,4)

options_count['without']= range(1,3)

for option,count_list in options_count.items():
    for count in count_list:
        acc_forces_per_task[option+str(count)]=[]
        durations_per_task[option+str(count)]=[]

#color_list = ['red', 'blue', 'green', 'orange', 'yellow']
#color_list_inkscape = [(210,68,66,255), (0,125,197,255), (112,146,91,255), (255,131,20,255), (253,185,19,255),(221,87,255,255), (15,224,230,255)]
color_list_inkscape = [ (0,125,197,255), (64,152,211,255), (148,188,228,255), (52,86,31,255),(82,116,61,255),(112,146,91,255),(148,171,130,255), (189,201,176,255)]

color_list = []
for tuple in color_list_inkscape:
    color_list.append(np.divide(np.asarray(tuple),255.))





color_count = 0

for VP_name in VP_list:
    fig_hist_force = None
    fig_hist_time = None
    participant_folder_name = VP_name + '/'
    with_folder_namen = [VP_name+'_with_1', VP_name+'_with_2', VP_name+'_with_3' ,VP_name+'_spline_with_1', VP_name+'_spline_with_2', VP_name+'_spline_with_3']
    without_folder_namen = [VP_name+'_without_1',VP_name+'_without_2',VP_name+'_spline_without_1',VP_name+'_spline_without_2']

    with_folder = fill_folder_list(with_folder_namen, spline=PLOT_SPLINE)
    without_folder = fill_folder_list(without_folder_namen, spline=PLOT_SPLINE)


    folder_paths_without = []
    for name in without_folder_namen:
        if participant_folder_name != '':
            folder_paths_without.append(userstudy_folder_path+participant_folder_name+name)
        else:
            folder_paths_without.append(userstudy_folder_path+name)
    folder_paths_with = []
    for name in with_folder_namen:
        if participant_folder_name != '':
            folder_paths_with.append(userstudy_folder_path+participant_folder_name+name)
        else:
            folder_paths_with.append(userstudy_folder_path+name)




    folder_paths = {'with': folder_paths_with, 'without': folder_paths_without}

    data = {}
    print ("starting to load data from " + userstudy_folder_path + participant_folder_name)
    for option_name, folder_option in folder_paths.items():
        #print "option name " +str(option_name)
        data[option_name]= {}
        for folder_path in folder_option:
            folder_name = folder_path.split('/')[-1]
            data[option_name][folder_name]={}
            for name in file_names:
                data_list = []
                file_name = folder_path+'/'+name+'.p'
                #print("file_name" , file_name)
                try:
                    with open(file_name, 'rb') as f:
                        count = 0
                        while True:
                            try:
                                loaded_data = pickle.load(f)
                                data_list.append(loaded_data)
                                #print(loaded_data)
                                count+=1
                            except:
                                #print ("exept for ", file_name)
                                #print (count)
                                break
                except:
                    print ("file not found: " +str(file_name))

                data[option_name][folder_name][name] = data_list
                #print(data_list[:10])
                #print ("**********************")
    print ("all data loaded for VP " +str(VP_name))


    all_data[VP_name] = data






    ###### different plots

    task_states = {}

    color_count = 0
    for option in ['with','without']:

        if PLOT_SPLINE and ((option == 'with' and not CONTROL) or CONTROL):
            task_states['PF'] = ['ring_grasped', 'transition_with_spline', 'goal_state']
            task_states['pick'] = ['init_state', 'start_state', 'close_to_ring', 'x_y_perfectly', 'valid_grasp_position']
            #task_states['pick'] = ['close_to_ring', 'x_y_perfectly', 'valid_grasp_position']
        elif PLOT_SPLINE and option == 'without' and not CONTROL:
            #task_states['pick'] = ['close_to_ring_pick', 'x_y_perfectly_over_ring', 'valid_grasp_position']
            task_states['pick'] = ['init_state_here', 'start_state_here', 'close_to_ring_pick', 'x_y_perfectly_over_ring', 'valid_grasp_position']
            task_states['PF'] = ['ring_grasped', 'transition_with_spline', 'goal_state']
        else:
            task_states['pick'] = ['init_state_here', 'start_state_here', 'close_to_ring_pick', 'x_y_perfectly_over_ring', 'valid_grasp_position']
            #task_states['pick'] = ['close_to_ring_pick', 'x_y_perfectly_over_ring', 'valid_grasp_position']

        task_states['place'] = ['enter_place', 'start_place', 'close_to_pin_place', 'over_pin', 'valid_release_position', 'placed']


        count = 0
        if option == 'with':
            selected_folder_type = with_folder
            with_forces = True
        else:
            selected_folder_type = without_folder
            with_forces = False





        #### plot poses over time



        if fig_hist_force is None:
            fig_hist_force = plt.figure()
            ax_force = fig_hist_force.add_subplot(111)
            fig_hist_torque = plt.figure()
            ax_torque = fig_hist_torque.add_subplot(111)
            fig_hist_time = plt.figure()
            ax_time = fig_hist_time.add_subplot(111)
            offset = [-0.1, 0.0, 0.1]
        else:
            offset = [-0.2, 0.2]
        count = 1
        without_count = 0

        if PLOT_SPLINE:
            ax_force.set_title('Accumulated Forces for each task' +str(VP_name) + ' with spline')
            ax_torque.set_title('Accumulated Torques for each task' +str(VP_name)+ ' with spline')
            ax_time.set_title('Duration for each task ' +str(VP_name) + 'with spline')
        else:
            ax_force.set_title('Accumulated Forces for each task' +str(VP_name))
            ax_torque.set_title('Accumulated Torques for each task' +str(VP_name))
            ax_time.set_title('Duration for each task ' +str(VP_name))

        for folder in selected_folder_type:

            if 'without' in folder:
                without_count += 1
                label = 'without ' + str(without_count)
            else:
                label = "with " + str(count)

            ###### forces
            normed_forces = norm_forces(np.asarray(data[option][folder]['fixture_forces_info1'])[:, 1])
            if 'without' in folder and 'spline' in folder and len(np.asarray(data[option][folder]['calculated_spline_forces_for_gripper_pos']).shape)>1:
                normed_forces_spline = norm_forces(np.asarray(data[option][folder]['calculated_spline_forces_for_gripper_pos'])[:, 1])
            else:
                normed_forces_spline = norm_forces(np.asarray(data[option][folder]['fixture_forces_info2'])[:, 1])
            forces_per_state = accumulate_forces_per_state(normed_forces, [l.split(' ')[0] for l in np.asarray(data[option][folder]['sct_data'])[:, 1]], normed_forces_spline)
            forces_per_task = add_task_wise(forces_per_state)

            if 'PF' in forces_per_task.keys():
                forces_per_task['PF'][1]=0



            ###### durations
            durations_dict = get_duration_per_state(
                [l.split(' ')[0] for l in np.asarray(data[option][folder]['sct_data'])[:, 0]],
                [l.split(' ')[0] for l in np.asarray(data[option][folder]['sct_data'])[:, 1]])

            durations_per_task[option + str(count)].append(durations_dict)


            if PLOT_PER_VP:
                forces_sorted = sorted(forces_per_task.items())
                states,forces = zip(*forces_sorted)
                #print (len(states))
                index = np.arange(0,len(states), 1)

                ax_force.bar(index + offset[count-1],np.asarray(forces)[:,0], width = 0.1, label = label, color = color_list[color_count])
                ax_force.set_ylabel('Forces in N')
                ax_force.set_xticks(index)
                ax_force.set_xticklabels(states)
                #ax_force.set_ylim(0,1.2)

                ax_torque.bar(index + offset[count-1],np.asarray(forces)[:,1], width = 0.1, label = label, color = color_list[color_count])
                ax_torque.set_ylabel('Torques in Nm')
                ax_torque.set_xticks(index)
                ax_torque.set_xticklabels(states)
                #ax_torque.set_ylim(0,1.2)


                #print durations_dict
                durations_sorted = sorted(durations_dict.items())
                states,duration = zip(*durations_sorted)

                ax_time.bar(index + offset[count-1],duration, width = 0.1, label = label, color = color_list[color_count])
                ax_time.set_ylabel('Time in s')
                ax_time.set_xticks(index)
                ax_time.set_xticklabels(states)





                fig_hist_force.savefig(save_fig_path +VP_name+ '_bar_forces.pdf')
                fig_hist_torque.savefig(save_fig_path +VP_name+ '_bar_torques.pdf')
                fig_hist_time.savefig(save_fig_path + VP_name+'_bar_times.pdf')

            count += 1
            color_count += 1








#print "acc forces per task " +str(acc_forces_per_task)
#print "durations " +str(durations_per_task)


summed_forces_per_task = collections.OrderedDict()
forces_per_task_dict = collections.OrderedDict()
errors = collections.OrderedDict()
summed_durations_per_task = {}
fig_hist_force = None
count = 1
without_count = 0
color_count = 0

keys_for_transition_not_active = collections.OrderedDict()

for key,forces_per_task_list in acc_forces_per_task.items():
    summed_forces_per_task[key] = {}
    forces_per_task_dict[key] = {}
    errors[key] = {}
    for forces_per_task in forces_per_task_list:
        for task in forces_per_task.keys():
            if task in summed_forces_per_task[key].keys():
                summed_forces_per_task[key][task] = np.add(summed_forces_per_task[key][task],forces_per_task[task])
                if  np.all(forces_per_task[task] == 0):
                    pass
                else:
                    forces_per_task_dict[key][task].append(forces_per_task[task])
            else:
                summed_forces_per_task[key][task] = copy.deepcopy(forces_per_task[task])
                if np.all(forces_per_task[task] == 0):
                    forces_per_task_dict[key][task] = []
                else:
                    forces_per_task_dict[key][task] = [forces_per_task[task]]



    if len(forces_per_task_list) > 0 :#and not( 'spline' in key and not PLOT_SPLINE):

        for task in forces_per_task_list[0].keys():
            count = 0
            for entry in summed_forces_per_task[key][task] :
                if not entry == 0:
                    if key in keys_for_transition_not_active.keys():
                        entry = np.divide(entry, keys_for_transition_not_active[key])
                    else:
                        entry = np.divide(entry, np.double(len(forces_per_task_dict[key][task])))
                    summed_forces_per_task[key][task][count] = copy.deepcopy(entry)

                else:
                    print ("cant divide by number of VP " +str(entry))
                    print (len(forces_per_task_dict[key][task]))
                count += 1
    else:
        print ("in else - not normalizing forces")
        continue




if not USE_PREDEFINED_MAX_WRENCH:
    max_wrench = {}
    for key, wrenches_per_task in summed_forces_per_task.items():
        for task in wrenches_per_task:
            if task in max_wrench.keys():
                if max_wrench[task][0]<wrenches_per_task[task][0]:
                    max_wrench[task][0] = wrenches_per_task[task][0]
                if max_wrench[task][1]<wrenches_per_task[task][1]:
                    max_wrench[task][1] = wrenches_per_task[task][1]
            else:
                max_wrench[task] = [wrenches_per_task[task][0],wrenches_per_task[task][1]]





for key, wrenches_per_task in summed_forces_per_task.items():
    for task in wrenches_per_task:
        if wrenches_per_task[task][0] != 0:
            wrenches_per_task[task][0] = np.divide(wrenches_per_task[task][0], max_wrench[task][0])
        if wrenches_per_task[task][1] != 0:
            wrenches_per_task[task][1] = np.divide(wrenches_per_task[task][1], max_wrench[task][1])
        for entry in forces_per_task_dict[key][task]:
            if entry[0] != 0:
                entry[0] = np.divide(entry[0], max_wrench[task][0])
            if entry[1] != 0:
                entry[1] = np.divide(entry[1], max_wrench[task][1])

for key, wrenches_per_task in summed_forces_per_task.items():

    for task in wrenches_per_task:
        if len(forces_per_task_dict[key][task])>1:
            errors[key][task] = [np.std(np.asarray(forces_per_task_dict[key][task])[:, 0]),np.std(np.asarray(forces_per_task_dict[key][task])[:, 1])]
        else:
            errors[key][task] =[0,0]


count = 1
without_count = 0
if CONTROL:
    color_count = 3
else:
    color_count = 0


for key in summed_forces_per_task.keys():
    #print "key " +str(key)
    if len(forces_per_task_list) < 0 or  'spline' in key:
        continue
    if fig_hist_force is None:
        fig_hist_force = plt.figure()
        ax_force = fig_hist_force.add_subplot(111)
        fig_hist_torque = plt.figure()
        ax_torque = fig_hist_torque.add_subplot(111)
        fig_hist_time = plt.figure()
        ax_time = fig_hist_time.add_subplot(111)
    if 'without' in key and not 'spline' in key:
        offset = [-0.2, 0.2]
        #print without_count
        offset_curr = offset[without_count]
        without_count +=1
        label = 'without ' +str(without_count)


    else:
        offset = [-0.2, -0.1, 0.0, 0.1, 0.2]
        offset_curr = offset[count]
        label = "with " +str(count)
        count +=1
    '''
    if PLOT_SPLINE:
        ax_force.set_title('Average Forces for each task with spline')
        ax_torque.set_title('Average Torques for each task with spline')
    else:
        ax_force.set_title('Average Forces for each task')
        ax_torque.set_title('Average Torques for each task')
    '''

    if len(summed_forces_per_task[key].keys())>0:
        #print summed_forces_per_task[key]
        forces_sorted = sorted(summed_forces_per_task[key].items())
        states,forces = zip(*forces_sorted)
        index = np.arange(0,3, 1)

        errors_sorted = sorted(errors[key].items())
        states,errors_sorted_to_plot = zip(*errors_sorted)
        ax_force.set_xticks(index)
        ind_count = 0
        for label in ['pick', 'PF', 'place']:
            if label in summed_forces_per_task[key].keys():

                forces_to_plot = summed_forces_per_task[key][label]
                errors_to_plot = errors[key][label]

                ax_force.bar(ind_count + offset_curr,np.asarray(forces_to_plot)[0],yerr= np.asarray(errors_to_plot)[0], width = 0.1, label = label, color = color_list[color_count],ecolor='black')
                if ( PLOT_SPLINE and not label == 'PF') or not PLOT_SPLINE:
                    ax_torque.bar(ind_count + offset_curr,np.asarray(forces_to_plot)[1],yerr= np.asarray(errors_to_plot)[1], width = 0.1, label = label, color = color_list[color_count],ecolor='black')

            ind_count +=1
        #ax_force.set_ylabel('Forces in N')


        ax_force.set_xticks(index)


        ax_force.set_ylim(0, 1.2)

        #ax_torque.bar(index + offset_curr,np.asarray(forces)[:,1],yerr= np.asarray(errors_sorted_to_plot)[:,1], width = 0.1, label = label, color = color_list[color_count],ecolor='black')
        #ax_torque.set_ylabel('Torques in Nm')

        ax_torque.set_xticks(index)
        if PLOT_SPLINE:
            ax_force.set_xticklabels(['pick', 'path_following', 'place'])
            ax_torque.set_xticklabels(['pick', '', 'place'])
        else:
            ax_force.set_xticklabels(['pick', '', 'place'])
            ax_torque.set_xticklabels(['pick', '', 'place'])


        ax_torque.set_ylim(0, 1.2)
        #ax_force.legend(loc='upper center', bbox_to_anchor=(0.5, -0.045),fancybox=True, shadow=False, ncol=5)
        #ax_torque.legend(loc='upper center', bbox_to_anchor=(0.5, -0.045),fancybox=True, shadow=False, ncol=5)
        color_count +=1






if PLOT_SPLINE:
    fig_hist_force.savefig(save_fig_path + 'bar_forces_with_spline.pdf', bbox_inches='tight')
    fig_hist_torque.savefig(save_fig_path + 'bar_torques_with_spline.pdf', bbox_inches='tight')
else:

    fig_hist_force.savefig(save_fig_path + 'bar_forces.pdf', bbox_inches='tight')
    fig_hist_torque.savefig(save_fig_path + 'bar_torques.pdf', bbox_inches='tight')


summed_durations_per_task = {}
durations_per_task_dict = {}
errors = {}
fig_hist_time = None
count = 1
without_count = 0
if CONTROL:
    color_count = 3
else:
    color_count = 0

for key,durations_per_task_list in durations_per_task.items():
    summed_durations_per_task[key] = {}
    durations_per_task_dict[key] = {}
    for duration_per_task in durations_per_task_list:
        for task in duration_per_task.keys():
            if task in summed_durations_per_task[key].keys():
                summed_durations_per_task[key][task] = np.add(summed_durations_per_task[key][task],duration_per_task[task])
                if duration_per_task[task] != 0:
                    durations_per_task_dict[key][task].append(duration_per_task[task])
            else:
                summed_durations_per_task[key][task] = copy.deepcopy(duration_per_task[task])
                if duration_per_task[task] != 0:
                    durations_per_task_dict[key][task] = [duration_per_task[task]]
                else:
                    durations_per_task_dict[key][task] = []


    if len(durations_per_task_list) > 0 and not( 'spline' in key and not PLOT_SPLINE):
        for task in duration_per_task.keys():
            if summed_durations_per_task[key][task] != 0:
                if key in keys_for_transition_not_active.keys():
                    summed_durations_per_task[key][task] = np.divide(summed_durations_per_task[key][task], keys_for_transition_not_active[key])

                else:
                    summed_durations_per_task[key][task] = np.divide(summed_durations_per_task[key][task], np.double(len(durations_per_task_dict[key][task])))


for key, durations_per_task_list in summed_durations_per_task.items():
    errors[key] = {}
    for task in durations_per_task_list:
        errors[key][task] = np.std(np.asarray(durations_per_task_dict[key][task]))

for key,durations_per_task_list in durations_per_task.items():
    if len(durations_per_task_list) < 0 or 'spline' in key:
        continue

    if fig_hist_time is None:
        fig_hist_time = plt.figure()
        ax_time = fig_hist_time.add_subplot(111)

    if 'without' in key and not 'spline' in key:
        offset = [-0.2, 0.2]
        offset_curr = offset[without_count]
        without_count +=1
        label = 'without ' +str(without_count)
    else:
        offset = [-0.2, -0.1, 0.0, 0.1, 0.2]
        offset_curr = offset[count]
        label = "with " +str(count)
        count +=1

    #times_sorted = sorted(summed_durations_per_task[key].items())
    #states,times = zip(*times_sorted)
    index = np.arange(0,3, 1)

    #errors_sorted = sorted(errors[key].items())
    #states, errors_sorted_to_plot = zip(*errors_sorted)


    ind_count = 0
    for label in ['pick', 'PF', 'place']:
        if label in summed_durations_per_task[key].keys():
            times_to_plot = summed_durations_per_task[key][label]
            errors_to_plot = errors[key][label]

            ax_time.bar(ind_count + offset_curr,np.asarray(times_to_plot),yerr= np.asarray(errors_to_plot), width = 0.1, label = label, color = color_list[color_count],ecolor='black')
        ind_count +=1

    ax_time.set_ylim(0, 60)
    ax_time.set_xticks(index)
    if PLOT_SPLINE:
        ax_time.set_xticklabels(['pick', 'path_following', 'place'])
    else:
        ax_time.set_xticklabels(['pick', '', 'place'])

    color_count +=1





if PLOT_SPLINE:
    fig_hist_time.savefig(save_fig_path + 'bar_times_with_spline.pdf', bbox_inches='tight')
else:
    fig_hist_time.savefig(save_fig_path + 'bar_times.pdf', bbox_inches='tight')


############ statistical analysis learning effect between first and fifth trial for each task

from scipy import stats



pick_1 = forces_per_task_dict['ohne1']['pick']
pick_5 = forces_per_task_dict['ohne2']['pick']
place_1 = forces_per_task_dict['ohne1']['place']
place_5 = forces_per_task_dict['ohne2']['place']

if len(place_1) != len(place_5):
    place_1 = [place_1[0], place_1[2]]

evaluate_PF = False
if 'PF' in forces_per_task_dict['ohne1'].keys():
    PF_1 = forces_per_task_dict['ohne1']['PF']
    PF_5 = forces_per_task_dict['ohne2']['PF']
    evaluate_PF = True

####################### translational
print '########### translational '

statistic, pvalue = stats.ttest_rel(np.asarray(pick_1)[:,0], np.asarray(pick_5)[:,0])
print "pick "
print statistic, pvalue


statistic, pvalue = stats.ttest_rel(np.asarray(place_1)[:,0], np.asarray(place_5)[:,0])

print "place "
print statistic, pvalue

if evaluate_PF:

    statistic, pvalue = stats.ttest_rel(np.asarray(PF_1)[:,0], np.asarray(PF_5)[:,0])
    print "PF "
    print statistic, pvalue



####################### roational


print '########### rotational '
statistic, pvalue = stats.ttest_rel(np.asarray(pick_1)[:,1], np.asarray(pick_5)[:,1])

print "pick "
print statistic, pvalue

statistic, pvalue = stats.ttest_rel(np.asarray(place_1)[:,1], np.asarray(place_5)[:,1])

print "place "
print statistic, pvalue


if evaluate_PF:

    statistic, pvalue = stats.ttest_rel(np.asarray(PF_1)[:,1], np.asarray(PF_5)[:,1])
    print "PF "
    print statistic, pvalue

