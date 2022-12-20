# About the work
We predict the optimal beam indices from a pre-defined codebook by utilizing a machine learning model and the position information ( Latitude and Longitude values ) of the transmitter.

![a](https://user-images.githubusercontent.com/80635318/208714173-86cc8bc7-7974-4847-8f2b-f75e5694f3a5.PNG)

# NN - Multi-layer Perceptron Classifier (MLPClassifier)

The multilayer perceptron (MLP) is a feedforward artificial neural network model that maps input data sets to a set of appropriate outputs.
An MLP consists of multiple layers and each layer is fully connected to the following one. 
![b](https://user-images.githubusercontent.com/80635318/208714544-083873c8-51b9-4bc7-b824-8df14a245f90.PNG)

## Steps:
#### 1. Data preprocessing:
![c](https://user-images.githubusercontent.com/80635318/208715109-75ca4f11-def7-4a2e-acf9-8935c8690aea.PNG)
As our task is predicting the optimal beam index from a given Latitude and Longitude coordinates .
These coordinates are saved under separate .txt files under the colomn "unit2_loc_1" . The final position dataset == the input of our MLP Classifier
We choose our features and our target and then perform train _ test _ split. To train a MLP network, the data should always be scaled because it is very sensitive to it.

#### 2. MLP Classifier & Training:

![d](https://user-images.githubusercontent.com/80635318/208715670-2f220176-ba04-44a5-8f07-cfd529397294.PNG)

- hidden_layer_sizes : With this parameter we can specify the number of layers and the number of nodes we want to have in the Neural Network Classifier. Each element in the tuple represents the number of nodes at the ith position, where i is the index of the tuple. Thus, the length of the tuple indicates the total number of hidden layers in the neural network.

- max_iter:   Indicates the number of epochs.

- activation: The activation function for the hidden layers.

- solver: This parameter specifies the algorithm for weight optimization over the nodes.

#### 3. Model Evaluation:
To evaluate our model we use Accuracy_score metric.
Ploting the loss curve:

![m](https://user-images.githubusercontent.com/80635318/208716043-c65b842d-6d57-468e-815a-5a8c7b62fff3.PNG)

Ploting the Confusion_matrix:
![n](https://user-images.githubusercontent.com/80635318/208716178-cdbc8e33-f1bd-4941-b5f8-14cc064815f2.PNG)



