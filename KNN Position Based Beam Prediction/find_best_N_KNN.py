# -*- coding: utf-8 -*-


import os
import train_test_func as func
# data probing, KNN and Lookup table intensive

# This folder should contain the outputs from loader.py
data_folder = os.path.join(os.getcwd(), 'Ready_data_norm1')

# Folder that will have this particular set of experiments 
experiment_folder = '' # '' uses the Hyperparemeters defined below on the name.


#%% Heaving KNN  Look-up table testing 

test_KNN_all_n = False

scen_idxs = np.arange(1,9+1)

for scen_idx in scen_idxs:
    
    # The saved folder will have all experiments conducted. 
    saved_path = join_paths([os.getcwd(), 'saved_folder', f'scenario {scen_idx}'])
    
    # Create dir if doesn't exist
    if not os.path.isdir(saved_path):
        os.mkdir(saved_path)
        
    # Load data from data_folder
    x_train = np.load(os.path.join(data_folder, f"scenario{scen_idx}_x_train.npy"))
    y_train = np.load(os.path.join(data_folder, f"scenario{scen_idx}_y_train.npy"))
    x_test = np.load(os.path.join(data_folder, f"scenario{scen_idx}_x_test.npy"))
    y_test = np.load(os.path.join(data_folder, f"scenario{scen_idx}_y_test.npy"))
    
    if test_KNN_all_n :
        vals_to_test = np.arange(1,100+1)
        n_vals_to_test = len(vals_to_test)
        
        # This is exactly as above, see the comments there.
        test_KNN_accs = np.zeros((n_vals_to_test, n_top_stats))
        for n_idx in range(n_vals_to_test):
            n = vals_to_test[n_idx]
            print(f'Doing KNN for n = {n:<2}')
            
            pred_beams = []
            
            np.random.seed(0)
            total_hits = np.zeros(n_top_stats)
            for sample_idx in range(n_test_samples):
                test_sample = x_test[sample_idx]
                test_label = y_test[sample_idx]
                
                distances = np.sqrt(np.sum((x_train - test_sample)**2, axis=1))
                
                neighbors_sorted_by_dist = np.argsort(distances)
                
                best_beams_n_neighbors = y_train[neighbors_sorted_by_dist[:n]]
                pred_beams.append(mode_list(best_beams_n_neighbors))
                
                for i in range(n_top_stats):
                    hit = np.any(pred_beams[-1][:top_beams[i]] == test_label)
                    total_hits[i] += 1 if hit else 0
            
            test_KNN_accs[n_idx] = total_hits / n_test_samples
        
        best_n = np.argmax(test_KNN_accs[:,0]) + 1
        # Plot the accuracy for each value of n
        f = plt.figure(figsize=(7,4), constrained_layout=True) # PUT BACK TO 7,4
        plt.plot(vals_to_test, np.round(test_KNN_accs*100,2))
        plt.legend([f"Top-{i} Accuracy" for i in top_beams], loc='upper right',
                    bbox_to_anchor=(1.36, 1.025))
        plt.xlabel('Number of neighbors')
        plt.ylabel('Accuracy')
        plt.title(f'Scenario {scen_idx} KNN Performance for all N (best N = {best_n})')
        plt.minorticks_on()
        plt.grid()
        plt.savefig(os.path.join(saved_path, f'KNN_test_all_N_scen{scen_idx}.pdf'),
                    bbox_inches = "tight")
        # bbox_inches = "tight" is needed if we are putting things outside the 
        # normal canvas size. This is what 'inline' in Spyder uses when displaying
    

        