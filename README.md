FDAOptimization
===============

Feature Decay Algorithms Optimization with Genetic Algorithms

Copyright (c) 2014, Ergun Bicici, <ergunbicici@yahoo.com>

Citation:

Ergun Bicici and Deniz Yuret, “Optimizing Instance Selection for Statistical Machine
Translation with Feature Decay Algorithms”, IEEE/ACM Transactions On Audio,
Speech, and Language Processing (TASLP), 2014.

Feature Decay Algorithms (FDA) is developed as part of my PhD thesis:

Ergun Biçici. The Regression Model of Machine Translation. PhD thesis, Koç University, 2011. Note: Supervisor: Deniz Yuret.


The program is using genetic algorithms (GA) for optimizing FDA. It uses inspyred package for optimization. 

TO RUN:
(1) Install the inspyred package:

    unzip inspyred.zip

    bash build_distribution.sh

    python setup.py install

(2) Prepare a config file for the optimization run. You can use the provided sample config file for this purpose: 

    fda.optimization.config

(3) Run an optimized fda:

    python runoptFDA.py

Sample run output is given in file samplerun.output and below:

optimization settings: ('../fda/fda', 'data/train.en', 'data/train.de', 'data/dev.en', 'data/dev.de', 2, 92681)
Optimization took: 5476.26002908
../fda/fda -v1 -t92681 -d1.0 -c1.0089124001 -s0.886387647059 -i2.16465456164 -l1.89379071178 -n2 -o fda.optimization.config.selection data/train.en data/dev.en data/train.de data/dev.de
FDA5 took: 37.7974550724
Overall time: 5514.05750203

