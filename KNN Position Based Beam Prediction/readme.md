## About the work

This work is related to the following article:

João Morais, and Ahmed Alkhateeb, "Position Aided Beam prediction: How useful GPS locations actually are?".

where we will use KNN- K Nearest Neighbors to predicted the beam indexes of the Millimeter-wave (mmWave) communication system.

## The Dataset

The data consists of Scenarios 1-9 of DeepSense6G dataset.

## Code Package Content:

You can find the folder that contains the 9 scenarios at "All_9_scenarios_datasets" folder.

In order to reproduce the work you should:

1. Run `pip install -r requirements.txt` (Python 2), or `pip3 install -r requirements.txt` (Python 3) to install all the requirements
2. Run `python KNN_model.py` to run the model

## Steps of the model

1. Fixe the number of neighbors ( N=30)

2. To make a prediction, we find the nearest neighbors to that input, and what their average output is.

3.  Calculate the Distances to each sample in training set

4.  Find the indices of the closest neighbors

5. Take the mode of the best beam of the n closest neighbors

![Capture](https://user-images.githubusercontent.com/80635318/208693748-6abb75c8-dad8-4366-8335-3496389a3e44.PNG)

# Results:
Here we display the results of the scenario 1 of the DeepSense6G dataset.
We used the following parameters of the model
- Nubmer of beams: `beams=64`
- Norm type: `norm=1`
- Number of the nearest neighbors: `n_KNN=30`
We computed the model's top_k accuracy where k=10 , which means in top-10 accuracy you give yourself credit for having the right answer if the right answer appears in your top 10 guesses.

![model](https://user-images.githubusercontent.com/80635318/208695924-64a29f19-c30d-4007-83b3-5effb2304801.PNG)


