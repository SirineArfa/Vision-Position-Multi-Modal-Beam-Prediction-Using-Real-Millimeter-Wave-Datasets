## Fusion schema architecture

![Capture](https://user-images.githubusercontent.com/80635318/208735892-eaf50098-abc4-4f68-a373-a620a252da4c.PNG)

## VGG16 model architecture

![2](https://user-images.githubusercontent.com/80635318/208737757-b2ea788d-4c67-43f8-843e-89cda8db33e6.PNG)

We used Pretrained VGG16 on imagenet weights for feature extraction for all the RGB camera's images of scenario5.
The result of the model is a feature vector with 4096 features.
The features vectors have many zeros. 
The zeros usually don’t add much information when computing similarity, but they occupy storage space, memory, and CPU.
We should reduce the dimensionality while preserving most of the data.
 --> we used Principal Component Analysis to reduce dimensionality.  We ended up using 785 components 
for dimensionality reduction.

## Image Feature Vectors Dataset
We have 151 row ( as we have worked with 150 images) and their coresponding 512 feature vactors.

![3](https://user-images.githubusercontent.com/80635318/208738550-6b726d5a-234a-41b4-a086-3289be91ba5a.PNG)

## Concatenation of visual and position data
We concatenate the user position data [Latitude, Longitude] with their corresponding beam_index and image feature vector.

## MLP classifier evaluation

![33](https://user-images.githubusercontent.com/80635318/208738894-533c0ec1-f120-4920-9046-3d98fb4805da.PNG)

## MLP Learning Curves

![Capture](https://user-images.githubusercontent.com/80635318/211220216-8d706e90-6ec1-4cd7-a7e5-7da14911f8d4.PNG)

