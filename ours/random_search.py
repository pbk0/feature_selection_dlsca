"""
Does random model search for ACADf, ASCADr and CHESCTF datasets.
Only OPOI datasets are used.

We experiment with different assumption for datasets while number of npoi's remain same.
Below are the differences.
+ validation dataset is not derived from attack dataset instead they used from profiling dataset
+ we shuffle dataset with determinist seed before splitting intro train and validate dataset
  + especially useful for CHESCTF dataset
+ we use standard normalization instead of z_score_norm that normalizes traces per sample
+ we perform model search using purely profiling traces without checking scores on attack datasets

We test below early stopping scenarios
+ none
+ val loss
+ rank loss
"""

