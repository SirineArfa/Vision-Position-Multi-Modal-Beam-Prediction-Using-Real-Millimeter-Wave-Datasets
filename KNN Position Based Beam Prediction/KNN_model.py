# -*- coding: utf-8 -*-


import os
import copy
import torch
import datetime
import itertools
import numpy as np
import pandas as pd

import train_test_func as func

# Folder with the outputs from loader.py:
gathered_data_folder = os.path.join(os.getcwd(), 'All_9_scenarios_datasets')
# Where every result folder will be saved too:
save_folder =  os.path.join(os.getcwd(), r'saved_folder\results')

# Variables to loop
ai_strategies = ['KNN']       # 'KNN'
norm_types = [1]                     # [1,2,3,4,5]
scen_idxs = np.arange(1,9+1)   # [1,2,3,4,5,6,7,9]
n_beams_list = [64]          # [8, 16,32,64]
noises = [0]                         # position noise in meters
n_reps = 1                           # number repetitions of current settings.

# Variables constant across simulation
use_cal_pos_for_scen = [3,4,8,9]        # [3,4,9] 8 also needs it!
max_samples = 1e5                     # max samples to consider per scenario
n_avgs = 1                           # number of runs to average
train_val_test_split = [60,20,20]     # 0 on val uses test set to validate.    
top_beams = np.arange(10) + 1  # Collect stats for Top X predictions
force_seed = -1                       # When >= 0, sets data randimzation 
                                      # seed. Useful for data probing.
                                      # Otherwise, seed = run_idx.

                
# KNN
n_knn = [30]                           # number of neighbors
use_best_n_knn = False                 # if True, ignores the value above.
BEST_N_PER_SCENARIO_KNN = \
    [5,24,65,28,9,5,13,80,54]         # best n measured in each scenario
                


# Plots
stats_on_data = False
data_probing_plots = False
lookup_table_plots = False
evaluate_predictors = False
plot_prediction_map = False

combinations = list(itertools.product(scen_idxs, n_beams_list, norm_types,n_knn,
                                      noises, [1 for i in range(n_reps)]))

for scen_idx, n_beams, norm_type,n_knn, noise, rep in combinations:
    
    print(f'Executing for scen={scen_idx}, beams={n_beams}, norm={norm_type}, n_KNN={n_knn}')
    
    data_folder = os.path.join(os.getcwd(), f'Ready_data_norm{norm_type}')
    
    # The saved folder will have all experiments conducted. 
    experiment_name = func.get_experiment_name(scen_idx, n_beams, norm_type, 
                                               noise)
    saved_path = os.path.join(save_folder, experiment_name)
                              
    
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)
    
    if not os.path.isdir(saved_path):
        os.mkdir(saved_path)
    
    # ----------------------- Phase 1: Data Loading ---------------------------
    # Files are: ['1_loc', '1_pwr', '2_loc']
    scen_str = f'scenario{scen_idx}'
    gathered_files = [f for f in os.listdir(gathered_data_folder)] 
    
    if scen_idx in use_cal_pos_for_scen:
        loc_str = "loc_cal"
    else:
        loc_str = "loc"
        
    pos1_path_aux = f"{scen_str}_unit1_loc" # assume unit 1 is static..
    pos2_path_aux = f"{scen_str}_unit2_{loc_str}"
    pwr1_path_aux = f"{scen_str}_unit1_pwr"
    
    pos1_file = [f for f in gathered_files if pos1_path_aux in f][0]
    pos2_file = [f for f in gathered_files if pos2_path_aux in f][0]
    pwr1_file = [f for f in gathered_files if pwr1_path_aux in f][0]
                 
    pos1_path = os.path.join(gathered_data_folder, pos1_file)
    pos2_path = os.path.join(gathered_data_folder, pos2_file)
    pwr1_path = os.path.join(gathered_data_folder, pwr1_file)
    
    # Position is N x 2; Power is N x 1 (best)
    pos1 = np.load(pos1_path)
    pos2 = np.load(pos2_path)
    pwr1 = np.load(pwr1_path)
    
    max_beams = pwr1.shape[-1]
    
    n_samples = min(len(pos2), max_samples)
    
    # -------------------- Phase 2: Data Preprocessing ------------------------
        
    # Trim altitudes if they exists
    pos1 = pos1[:,:2]
    pos2 = pos2[:,:2]
    
    # Insert Noise if enabled.
    pos2_with_noise = func.add_pos_noise(pos2, noise_variance_in_m=noise)
    
    if stats_on_data:
        func.get_stats_of_data([6], pos1, pos2_with_noise, pwr1, scen_idx)
    
    # Normalize position
    pos_norm = func.normalize_pos(pos1, pos2_with_noise, norm_type)
    
    # Assign beam values (and automatically downsample if n_beams != 64)
    if n_beams not in [8, 16, 32, 64]:
        raise Exception('')
    
    divider = max_beams // n_beams
    beam_idxs = np.arange(0, max_beams, divider)
    
    # Select alternating samples (every 2, 4 or 8)
    beam_pwrs = pwr1[:,beam_idxs]
    # Convert beam indices. 32 beams: ([0,2,4,..., 62]) -> [0,1,2,... 32]
    beam_data = np.argmax(beam_pwrs, axis=1)
        
    # ----------------- Phase 3: Define Path for run --------------------------
    
    # We first define the folder where results from this run will be saved
    # In that folder there will be other runs too, and that will tell us what's
    # the index of this run. That information is used to shuffle the data 
    # in a reproducible way. Run 1 uses seed 1, run 2 uses seed 2, etc.
    
    for ai_strategy in ai_strategies:
        
        # Compute parameters needed for setting runs_folder name
        # The Runs Folder contains the folders of each run.
        if ai_strategy == 'KNN':
            if use_best_n_knn:
                n = BEST_N_PER_SCENARIO_KNN[scen_idx-1]
            else:    
                n = n_knn
            runs_folder_name = f'KNN_N={n}'
        
        runs_folder = os.path.join(saved_path, runs_folder_name)
        
        # Create if doesn't exist
        if not os.path.isdir(runs_folder):
            os.mkdir(runs_folder)
            
        # Experiment index: number of experiments already conducted + 1
        run_idx = 1 + sum(os.path.isdir(os.path.join(runs_folder, run_folder))
                          for run_folder in os.listdir(runs_folder))
        
        now_time = datetime.datetime.now().strftime('Time_%m-%d-%Y_%Hh-%Mm-%Ss')
        
        run_folder = os.path.join(runs_folder, f"{run_idx}-{now_time}")
        
        # Check if there are enough runs. If yes, skip data loading, model
        # training and testing, and jump to averaging the results.
        if run_idx > n_avgs:
            print('Already enough experiments conducted for ' 
                  'this case. Either increase n_avgs, or try '
                  'a different set of parameters. SKIPPING TO the avg. '
                  'computation!')
        else:
            # -------------------- Phase 4: Split Data ------------------------
            
            # Create folder for the run
            os.mkdir(run_folder)
            
            # Shuffle Data (fixed, for reproducibility)
            if force_seed >= 0:
                np.random.seed(force_seed)
            else:
                np.random.seed(run_idx)
            sample_shuffle_list = np.random.permutation(n_samples)
            
            # Select sample indices for each set
            first_test_sample = int((1-train_val_test_split[2]) / 100 * n_samples)
            train_val_samples = sample_shuffle_list[:first_test_sample]
            test_samples = sample_shuffle_list[first_test_sample:]
            
            # (We have no use for x_val in KNN.)
            # CHOICE: we used train+val(80%) sets to train in KNN and the LUtable
            #         but in the NN we used only train(60%). This seemed a fair
            #         approach, and doing otherwise yields little difference.
            if train_val_test_split[1] == 0 or ai_strategy in ['LT']:
                train_samples = train_val_samples
                val_samples = test_samples
            else:
                train_ratio = np.sum(train_val_test_split[:2]) / 100
                first_val_sample = int(train_val_test_split[1] / 100 * 
                                       len(train_val_samples) / train_ratio)
                val_samples = train_val_samples[:first_val_sample]
                train_samples = train_val_samples[first_val_sample:]
            
            x_train = pos_norm[train_samples]
            y_train = beam_data[train_samples]
            x_val = pos_norm[val_samples]
            y_val = beam_data[val_samples]
            x_test = pos_norm[test_samples]
            y_test = beam_data[test_samples]
            y_test_pwr = beam_pwrs[test_samples]
            
            func.print_number_of_samples(x_train, x_val, x_test, 
                                          y_train, y_val, y_test)
            
            filename = os.path.join(run_folder, 
                                      scen_str + f'_{n_beams}_{norm_type}')
            func.save_data(train_val_test_split, filename, 
                            x_train, x_val, x_test, y_train, y_val, y_test, 
                             y_test_pwr)
        
        # ---------------------- Phase 5: Train & Test ------------------------    
        
            # Useful little variables
            n_test_samples = len(x_test)
            n_top_stats = len(top_beams)
            
            # Variables for compatibility (when not all predictors are used)
            n_bins, bin_size, prediction_per_bin = None, None, None
            trained_model = None
        
        # 1- KNN
        if ai_strategy == 'KNN' and run_idx <= n_avgs:
            # Rationale: pick a number of neighbors. To make a prediction, we find
            # the nearest neighbors to that input, and what their average output is. 
            pred_beams = []
            for sample_idx in range(n_test_samples):
                test_sample = x_test[sample_idx]
                test_label = y_test[sample_idx]
                
                # Distances to each sample in training set
                distances = np.sqrt(np.sum((x_train - test_sample)**2, axis=1))
                
                # Find the indices of the closest neighbors
                neighbors_sorted_by_dist = np.argsort(distances)
                
                # Take the mode of the best beam of the n closest neighbors
                best_beams_n_neighbors = y_train[neighbors_sorted_by_dist[:n]]
                pred_beams.append(func.mode_list(best_beams_n_neighbors))
                
            
           
           
        
        # ----------- Phase 6: Save Accuracies and Power Losses ---------------
        if run_idx <= n_avgs:
            # Get top-1, top-2, top-3 and top-5 accuracies
            total_hits = np.zeros(n_top_stats)
            # For each test sample, count times where true beam is in top 1,2,3,5
            for i in range(n_test_samples):
                for j in range(n_top_stats):
                    hit = np.any(pred_beams[i][:top_beams[j]] == y_test[i])
                    total_hits[j] += 1 if hit else 0
            
            # Average the number of correct guesses (over the total samples)
            acc = np.round(total_hits / n_test_samples, 4)
            
            print(f'{ai_strategy} Results:')
            for i in range(n_top_stats):
                print(f'\tAverage Top-{top_beams[i]} accuracy {acc[i]*100:.2f}')
                    
            # Save Test acc to file
            np.savetxt(os.path.join(run_folder, 'test_accs.txt'), 
                       acc * 100, fmt='%.2f')
            
            # We consider the noise per sample, not per scenario:
            # Noise is the lowest power in each sample.
            power_loss_ratio = np.zeros(n_test_samples)
            for i in range(n_test_samples):
                noise = np.min(y_test_pwr[i,:]) / 2 
                
                pred_pwr = y_test_pwr[i,pred_beams[i][0]]
                true_pwr = np.max(y_test_pwr[i,:])
                
                if pred_pwr == noise:
                    # In Lookup table it may be the case we predict the worst
                    # beam to be the best. In this case, adjust noise slightly
                    # just to avoid -inf dB loss. This is extremely rare and
                    # will not affect results noticeably. 
                    noise = noise/2
                
                power_loss_ratio[i] = ((true_pwr - noise) / 
                                       (pred_pwr - noise))
                
            mean_power_loss_db = 10 * np.log10(np.mean(power_loss_ratio))
            
            print(f"{mean_power_loss_db:.4f}")
            
            np.savetxt(os.path.join(run_folder, 'power_loss.txt'),
                       np.stack((mean_power_loss_db, 0))) # needs to be 1D..
                
            
        # -------------- Phase 7: Compute average across runs ----------------
        if run_idx >= n_avgs:
            folders_of_each_run = [os.path.join(runs_folder, folder) 
                                   for folder in os.listdir(runs_folder)]
            
            folders_of_each_run = [folder for folder in folders_of_each_run 
                                   if os.path.isdir(folder)]
                           
            n_run_folders = len(folders_of_each_run)
            val_accs = np.zeros((n_run_folders, len(top_beams)))
            test_accs = np.zeros((n_run_folders, len(top_beams)))
            mean_power_losses = np.zeros(n_run_folders)
            for run_idx in range(n_run_folders):
                run_folder = folders_of_each_run[run_idx]
                test_accs_file = os.path.join(run_folder, 'test_accs.txt')
                pwr_loss_file = os.path.join(run_folder, 'power_loss.txt')
                
              
            
            print(f'Computing the average of {n_run_folders} runs. ')
            
            # Write results to same text file
            func.write_results_together(ai_strategy, top_beams, runs_folder,
                                        n_run_folders, val_accs, 
                                        test_accs, mean_power_losses)
            
            func.write_results_separate(top_beams, runs_folder, n_run_folders,
                                        val_accs, test_accs, mean_power_losses)
            

        # ----------- Phase 8: Plot Statistics on each AI strategy ------------
        
        ######## Specific Predictor evaluation ########
   
                
        ######## General Predictor evaluation ########
        if evaluate_predictors:
            evaluations = ['confusion_matrix', 'prediction_error',
                           'prediction_error2', 'positions_colored_by_error']
            func.evaluate_predictors(evaluations, pred_beams, x_test, y_test, 
                                     n_beams, scen_idx, ai_strategy, n, run_folder)
            
        if plot_prediction_map:
            N = 1e5
            func.prediction_map(N, ai_strategy, n_beams, scen_idx, run_folder,
                                x_train, y_train, x_test, n, prediction_per_bin, 
                                bin_size, n_bins, trained_model)
        
        ######## Dataset probing (visualize data and assess biases) ########
        if data_probing_plots:
            training_or_testing_sets = ['full'] # ['train', 'val', 'test', 'full']
            
            # data_plots = ['position_color_best_beam', 
            #               'position_color_best_beam_polar',
            #               'beam_freq_histogram']
            
            data_plots = ['position_color_best_beam']
            
            func.plot_data_probing(training_or_testing_sets, data_plots, 
                                   ai_strategy, n_beams, runs_folder, scen_idx,
                                   norm_type, x_train, y_train, x_val, 
                                   y_val, x_test, y_test)
            
#%%    
if True:
# code to put excel together.
    # Variables to loop
    stats_to_collect = ['val_acc', 'test_acc', 'pwr']
    
    # Create a column in the CSV for each result. 
    
    # Fixed variables
    target_filename = 'avg_results_of_{n_avgs}'
    
    l_scen = len(scen_idxs)
    l_beam = len(n_beams_list) 
    l_strat = len(ai_strategies) 
    l_norm = len(norm_types) 
    l_noise = len(noises)
    n_rows = l_scen * l_beam * l_strat * l_norm * l_noise
    n_cols = len(top_beams) * 4 + 2
    
    row_names = ['' for i in range(n_rows)]
    all_data = np.zeros((n_rows, n_cols))
    
    # Loop across all folders and pick the corresponding files with the results
    # + Save the results to all_data array
    
    combinations = list(itertools.product(ai_strategies, scen_idxs, n_beams_list, 
                                          norm_types, noises))
    for ai_strat, scen_idx, n_beams, norm_type, noise in combinations:
        ai_strat_idx = ai_strategies.index(ai_strat)
        norm_idx = norm_types.index(norm_type)
        n_beams_idx = n_beams_list.index(n_beams)
        noise_idx = noises.index(noise)
        scen_idx_idx = list(scen_idxs).index(scen_idx)
        
        
        row_idx = (ai_strat_idx * l_norm * l_scen * l_beam * l_noise + 
                   norm_idx * l_scen * l_beam * l_noise + 
                   n_beams_idx * l_scen * l_noise + 
                   noise_idx * l_scen + 
                   scen_idx_idx)
        
        experiment_folder_name = \
            func.get_experiment_name(scen_idx, n_beams, norm_type, noise)
        
        # Each row will have the name of the ai strategy and experiment
        row_names[row_idx] = f"{ai_strat} " + experiment_folder_name
        experiment_folder = os.path.join(save_folder, experiment_folder_name)
        
        # list folders in this directory match AI strat folder
        # there should be only one folder that starts with the name
        # of each AI strategy
        predictors_foldername = \
            [folder for folder in os.listdir(experiment_folder)
             if ai_strat == folder[:len(ai_strat)]][0]
        
        pred_folder = os.path.join(experiment_folder, 
                                   predictors_foldername)
        
        # print(f'{ai_strat}_beams-{n_beams}_scen-{scen_idx}_norm-{norm_type}_'
        #       f'noise-{noise} - ROW {row_idx} - '
        #       f'folder = {predictors_foldername} ')
        for stat in stats_to_collect:
            # Get the index of the first component. 
            #    4x val + 4x test + 1 power
            if 'acc' in stat:
                col_idx = len(top_beams) if stat == 'test_acc' else 0
                # collect data from this experiment:
                for i, top in enumerate(top_beams):
                    idx = col_idx + i
                    file = f"{n_avgs}-runs_top-{top}_" + stat + ".txt"
                    file_path = os.path.join(pred_folder, file)
                    mean_and_std = np.loadtxt(file_path)
                    # print(f'row: {row_idx}, col: {idx}')
                    all_data[row_idx, idx] = mean_and_std[0]
                    all_data[row_idx, idx+n_cols//2] = mean_and_std[1]
            else:
                col_idx = len(top_beams)*2
                file = f"{n_avgs}-runs_mean_power_loss_db.txt"
                file_path = os.path.join(pred_folder, file)
                mean_and_std = np.loadtxt(file_path)
                # print(f'row: {row_idx}, col: {col_idx}')
                all_data[row_idx, col_idx] = mean_and_std[0]
                all_data[row_idx, col_idx+n_cols//2] = mean_and_std[1]

    # Prepare column names                        
    mean_col_names = []
    for stat, top_beam in list(itertools.product(stats_to_collect, top_beams)):
        if 'acc' in stat:
            col_name = f"top-{top_beam}_{stat}_mean"
        else:
            col_name = f"{stat}_mean"
            if col_name in mean_col_names:
                continue
        mean_col_names.append(col_name)
    std_col_names = []
    for col_name in mean_col_names:
        std_col_names.append(col_name.replace('_mean', '_std'))
    col_names = mean_col_names + std_col_names                         
    
    if len(col_names) != n_cols:
        raise Exception('Col_names does not match number of columns in data.')
    
    # Write rows and columns to dataframe
    df = pd.DataFrame(all_data, columns=col_names)
    # Write column called experiment
    df.insert(0, "experiment", row_names)
    # Save the dataframe to csv file (2 copies, actually)
    now_time = datetime.datetime.now().strftime('%m-%d-%Y_%Hh-%Mm-%Ss')
    df.to_csv(os.path.join(save_folder, 'results_' + now_time + '.csv'), index=False)
    # df.to_csv('last_results.csv', index=False)
