### this is not an official report
### this file serves as a data dump for various model implementation during work on the project
### for official report, open the file ???? TODO

#=== REPORT ===

note: this run was test of new logging function
memo: basic DQN, training done in batches, no normalisation, only one NN, random batches for better learning
Number of episodes: 200
Buffer size: 3000
Batch size: 64
Gamma: 0.99
Learning rate: 0.001

## Mean rewards

#=== REPORT ===

note: another test of logging function
memo: basic DQN, training done in batches, no normalisation, only one NN, random batches for better learning
Number of episodes: 200
Buffer size: 3000
Batch size: 64
Gamma: 0.99
Learning rate: 0.001

## Mean rewards

- Episode 0.0: -48.52
- Episode 50.0: -155.52
- Episode 100.0: -172.56
- Episode 150.0: -175.01
#================

#during training phase betterment of NN will be evaluated on 5000 episodes test runs 

#=== REPORT: LOG UPDATE TEST ===

note: test if program will work after changes in logging function
memo: basic DQN, training done in batches, no normalisation, only one NN, random batches for better learning
NN Layout: 8->64->RELU->64->RELU->4 (two hidden layers of 64 neurons, ReLU activation function, MSE loss function)
Number of episodes: 200
Buffer size: 3000
Batch size: 64
Gamma: 0.99
Learning rate: 0.001

## Mean rewards

- Episode 0.0: -83.63, epsilon: 1.00
- Episode 50.0: -174.24, epsilon: 0.99
- Episode 100.0: -174.25, epsilon: 0.99
- Episode 150.0: -178.28, epsilon: 0.98
#================

#=== REPORT: INITIAL NN test results ===

note: this was initial test of neural network, without improvements like normalising the inputs, rewards were steadely decreasing which is concerning
memo: basic DQN, training done in batches, no normalisation, only one NN, random batches for better learning
NN Layout: 8->64->RELU->64->RELU->4 (two hidden layers of 64 neurons, ReLU activation function, MSE loss function)
Number of episodes: 5000
Buffer size: 3000
Batch size: 64
Gamma: 0.99
Learning rate: 0.001

## Mean rewards

- Episode 0.0: -106.05, epsilon: 1.00
- Episode 50.0: -164.12, epsilon: 0.99
- Episode 100.0: -197.53, epsilon: 0.99
- Episode 150.0: -174.88, epsilon: 0.98
- Episode 200.0: -168.35, epsilon: 0.98
- Episode 250.0: -179.02, epsilon: 0.97
- Episode 300.0: -178.44, epsilon: 0.97
- Episode 350.0: -193.75, epsilon: 0.96
- Episode 400.0: -220.68, epsilon: 0.96
- Episode 450.0: -220.26, epsilon: 0.95
- Episode 500.0: -195.68, epsilon: 0.95
- Episode 550.0: -189.42, epsilon: 0.94
- Episode 600.0: -188.83, epsilon: 0.94
- Episode 650.0: -193.36, epsilon: 0.93
- Episode 700.0: -223.73, epsilon: 0.93
- Episode 750.0: -187.30, epsilon: 0.92
- Episode 800.0: -194.66, epsilon: 0.92
- Episode 850.0: -172.98, epsilon: 0.91
- Episode 900.0: -209.73, epsilon: 0.91
- Episode 950.0: -215.07, epsilon: 0.90
- Episode 1000.0: -208.73, epsilon: 0.90
- Episode 1050.0: -197.42, epsilon: 0.89
- Episode 1100.0: -186.32, epsilon: 0.89
- Episode 1150.0: -207.49, epsilon: 0.88
- Episode 1200.0: -185.72, epsilon: 0.88
- Episode 1250.0: -198.86, epsilon: 0.87
- Episode 1300.0: -226.90, epsilon: 0.87
- Episode 1350.0: -198.97, epsilon: 0.86
- Episode 1400.0: -256.87, epsilon: 0.86
- Episode 1450.0: -202.47, epsilon: 0.85
- Episode 1500.0: -210.02, epsilon: 0.85
- Episode 1550.0: -209.26, epsilon: 0.84
- Episode 1600.0: -226.01, epsilon: 0.84
- Episode 1650.0: -226.25, epsilon: 0.83
- Episode 1700.0: -208.03, epsilon: 0.83
- Episode 1750.0: -235.35, epsilon: 0.82
- Episode 1800.0: -239.24, epsilon: 0.82
- Episode 1850.0: -188.55, epsilon: 0.81
- Episode 1900.0: -240.72, epsilon: 0.81
- Episode 1950.0: -235.43, epsilon: 0.80
- Episode 2000.0: -217.32, epsilon: 0.80
- Episode 2050.0: -224.13, epsilon: 0.79
- Episode 2100.0: -216.60, epsilon: 0.79
- Episode 2150.0: -227.20, epsilon: 0.78
- Episode 2200.0: -260.57, epsilon: 0.78
- Episode 2250.0: -250.02, epsilon: 0.77
- Episode 2300.0: -262.05, epsilon: 0.77
- Episode 2350.0: -249.28, epsilon: 0.76
- Episode 2400.0: -264.95, epsilon: 0.76
- Episode 2450.0: -256.70, epsilon: 0.75
- Episode 2500.0: -273.27, epsilon: 0.75
- Episode 2550.0: -259.98, epsilon: 0.74
- Episode 2600.0: -266.38, epsilon: 0.74
- Episode 2650.0: -264.20, epsilon: 0.73
- Episode 2700.0: -290.07, epsilon: 0.73
- Episode 2750.0: -256.01, epsilon: 0.72
- Episode 2800.0: -300.10, epsilon: 0.72
- Episode 2850.0: -264.55, epsilon: 0.71
- Episode 2900.0: -298.84, epsilon: 0.71
- Episode 2950.0: -269.53, epsilon: 0.70
- Episode 3000.0: -298.08, epsilon: 0.70
- Episode 3050.0: -305.86, epsilon: 0.69
- Episode 3100.0: -250.43, epsilon: 0.69
- Episode 3150.0: -258.58, epsilon: 0.68
- Episode 3200.0: -308.22, epsilon: 0.68
- Episode 3250.0: -298.34, epsilon: 0.67
- Episode 3300.0: -295.55, epsilon: 0.67
- Episode 3350.0: -313.14, epsilon: 0.66
- Episode 3400.0: -296.77, epsilon: 0.66
- Episode 3450.0: -279.00, epsilon: 0.65
- Episode 3500.0: -315.70, epsilon: 0.65
- Episode 3550.0: -301.75, epsilon: 0.64
- Episode 3600.0: -300.50, epsilon: 0.64
- Episode 3650.0: -300.79, epsilon: 0.63
- Episode 3700.0: -282.85, epsilon: 0.63
- Episode 3750.0: -300.07, epsilon: 0.62
- Episode 3800.0: -317.91, epsilon: 0.62
- Episode 3850.0: -312.92, epsilon: 0.61
- Episode 3900.0: -334.88, epsilon: 0.61
- Episode 3950.0: -334.41, epsilon: 0.60
- Episode 4000.0: -356.07, epsilon: 0.60
- Episode 4050.0: -365.20, epsilon: 0.59
- Episode 4100.0: -302.61, epsilon: 0.59
- Episode 4150.0: -332.14, epsilon: 0.58
- Episode 4200.0: -332.72, epsilon: 0.58
- Episode 4250.0: -324.08, epsilon: 0.57
- Episode 4300.0: -321.05, epsilon: 0.57
- Episode 4350.0: -315.13, epsilon: 0.56
- Episode 4400.0: -344.64, epsilon: 0.56
- Episode 4450.0: -342.14, epsilon: 0.55
- Episode 4500.0: -319.19, epsilon: 0.55
- Episode 4550.0: -292.00, epsilon: 0.54
- Episode 4600.0: -322.70, epsilon: 0.54
- Episode 4650.0: -353.54, epsilon: 0.53
- Episode 4700.0: -323.84, epsilon: 0.53
- Episode 4750.0: -298.75, epsilon: 0.52
- Episode 4800.0: -380.70, epsilon: 0.52
- Episode 4850.0: -343.02, epsilon: 0.51
- Episode 4900.0: -389.65, epsilon: 0.51
- Episode 4950.0: -307.89, epsilon: 0.50
#================

