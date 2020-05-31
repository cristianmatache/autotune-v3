# Autotune-v2

[![<ORG_NAME>](https://circleci.com/gh/cristianmatache/autotune-v2.svg?style=svg)](https://circleci.com/gh/cristianmatache/autotune-v2)

### Abstract
Performance of machine learning models relies heavily on finding a good combination of hyperparameters. We aim to design the most efficient hybrid between two best-in-class hyperparameter
optimizers, Hyperband and TPE. On the way there, we identified and solved a few problems:

1. Typical metrics for comparing optimizers are neither quantitative nor informative about how
well an optimizer generalizes over multiple datasets or models.
2. Running an optimizer several times to collect performance statistics is time consuming/impractical.
3. Optimizers can be flawed: implementation-wise (eg. virtually all Hyperband implementations) or design-wise (eg. first published Hyperband-TPE hybrid).
4. Optimizer testing has been impractical because testing on true ML models is time-consuming.

To overcome these challenges, we propose: *Gamma loss function simulation*, *Closest known loss
function approximation* and a more comprehensive set of metrics. All three are benchmarked
against published results on true ML models. The simulation and the approximation complement
each other: the first makes testing practical for the first time and serves as a theoretical ML model
while the latter allows for timely collection of statistics about optimizer performance as if it was
run on a true ML model.

Finally, we use these to find the best hybrid architecture which is validated by comparison with
Hyperband and TPE on 2 datasets and several mathematical hard-to-optimize functions. The
pursuit for a hybrid is legitimate since it outperforms Hyperband and TPE alone, but there is still
some distance to the state-of-the-art performances.


**Keywords:** hyperparameter optimizer design, Hyperband-TPE hybrid, instant optimizer testing,
instant loss function simulation, loss function approximation, optimizer evaluation, deep learning


## Associated works
- *Efficient design of Machine Learning hyperparameter optimizers.* Cristian Matache, Dr. Jonathan Passerat-Palmbach, Dr. Bernhard Kainz. Imperial College London 2019 
https://www.imperial.ac.uk/media/imperial-college/faculty-of-engineering/computing/public/1819-ug-projects/MatacheC-Efficient-Design-of-Machine-Learning-Hyperparameter-Optimizers.pdf
- *Gamma Loss Functions: Enabling Instant Testing, Debugging and Monitoring of AutoML Methods* Cristian Matache, Dr. Jonathan Passerat-Palmbach, Dr. Juste Raimbault, Dr. Romain Reuillon, Dr. Daniel Rueckert
TODO URL

## Preview
#### 1. Better optimizer metrics: EPDF-OFEs
Example loss functions | Example optimal final error (OFE)
--------------------------------|----------------------------------
<img src="https://github.com/cristianmatache/autotune-v2/blob/master/static/loss-function-profiles.png" width="300"> | <img src="https://github.com/cristianmatache/autotune-v2/blob/master/static/best-result-metric.png" width="300">
Several profiles e.g. mean, std, order |  Lowest final error of all loss functions:

We are therefore characterizing an optimizer by its estimated probability density function of optimal final errors (EPDF-OFE).
This would give us more meaningful quantitative measures like statistical significance.
Example:

Histogram of OFEs occurrences                                                                         |  Estimated PDFs
:----------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------:
<img src="https://github.com/cristianmatache/autotune-v2/blob/master/static/pdf-ofe-hb-tpe-2tpe-hist.png" width="300">|<img src="https://github.com/cristianmatache/autotune-v2/blob/master/static/pdf-ofe-hb-tpe-2tpe-pdf-ofe.png" width="300">

*Problem:* One needs to run the optimizer several times to find its EPDF-OFE which is very time consuming (order of years) if done on the pure underlying ML model since 
it requires retraining. *Solved later* 

#### 2. Implementations of otimizers can be flawed
Testing optimizers is usually done on some known hard-to-optimize function like Rastrigin. 
Testing on real ML models is much more difficult due to prolonged times of retraining the models several times for each optimization. 
Hence, for hyperparameter optimizers that employ early stopping there is virtually no way of testing comprehensively. 
This is problematic since **popular optimizers have flawed implementations**.

**Example flaw - Hyperband:**
We found that several Hyperband implementations suffer from a floating point arithmetic bug. This minor bug has impactful consequences:
- Less exploration (up to an order of magnitude)
- Wasting time and computing resources heavily

**Some of the flawed Hyperband implementations as of Sep 2019:**
1. https://homes.cs.washington.edu/˜jamieson/hyperband .html used by Hyperband authors (Li et al., 2016)
2. https://github.com/automl/HpBandSter/blob/367b6c42 03a63ff8b395740995b22dab512dcfef/hpbandster/ optimizers/hyperband.py#L60usedbyBOHB (Falkner et al., 2018). 
3. https://github.com/zygmuntz/hyperband/blob/master/ hyperband.py#L18 
4. https://gist.github.com/PetrochukM/2c5fae9daf0529ed 589018c6353c9f7b#ﬁle-hyperband-py-L204 
5. https://github.com/electricbrainio/hypermax/blob/mast er/hypermax/algorithms/adaptive bayesian hyperband optimizer.py#L26 
6. https://github.com/polyaxon/polyaxon/blob/c8bc14e92 b45579ecc19f2e51ae161f84d35d817/polyaxon/hpsearc h/search managers/hyperband.py#L58 
7. https://github.com/thuijskens/scikithyperband/blob/master/hyperband/search.py#L346


#### 3. Testing optimizers: Gamma loss function simulations
There is a clear need for more comprehensive testing of optimizers, especially for those that employ early stopping. 
We propose a method based on **Gamma processes** to simulate the loss functions in negligible time in order to test optimizers in several cases.
TODO

#### 3. Approximation: Closest loss function in terms of MSE
TODO

#### 4. Hyperband-TPE hybrids
TODO

## Preliminaries
Gaussian processes| Hyperband
------------------|----------
<img src="https://github.com/cristianmatache/autotune-v2/blob/master/static/gaussian-processes.png" width="300">|<img src="https://github.com/cristianmatache/autotune-v2/blob/master/static/hyperband-table.PNG" width="300">
