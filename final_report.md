# Reinforcement Learning with a Multilayer Neural Network for the Lander Control Problem

#### Mateusz Grodecki, 198385

The main goal of this project was to solve the lander control problem using reinforcement learning, artificial neural networks, and the Deep Q-Learning approach.

The project was implemented in Python using the Gymnasium environment and the PyTorch library. During development, several successful agents were trained according to the Gymnasium scoring criteria. The final version of the program allows the user to train, save, load, evaluate, and compare multiple learned policies.

---

## Main Concepts

The chosen learning method was Q-Learning. In classical tabular Q-Learning, the agent stores estimated values of actions in a Q-table and updates them using the formula:

```text
Q(s, a) <- Q(s, a) + α * (target - Q(s, a))

target = r + γ * max Q(s', a')
```

where:

- `s` — current state,
- `a` — selected action,
- `r` — reward received after the action,
- `s'` — next state,
- `α` — learning rate,
- `γ` — discount factor.

This approach works well for environments with a finite and relatively small number of states, such as movement on a small 2D grid. However, the LunarLander problem uses continuous observations, so storing every possible state in a table is not realistic.

Because of that, the tabular Q-table was replaced with a neural network. The network takes the current observation as input and returns estimated Q-values for all possible actions.

---

## Main Issues and Improvements

### Replacing the Q-table with a neural network

In Deep Q-Learning, the neural network works as a Q-value approximator. Instead of storing values for all states in a table, the model learns to estimate them.

The input of the network is the current observation from the environment, and the output contains Q-values for available actions. During exploitation, the action with the highest Q-value is selected.

---

### Replay buffer rework

Initially, the replay buffer was implemented as a Python list. This worked for small experiments, but became inefficient when the buffer reached full capacity.

The main issue was using:

```python
pop(0)
```

to remove the oldest experience. This operation has `O(n)` complexity because all remaining elements have to be shifted.

To solve this problem, the buffer was rewritten as a circular buffer based on NumPy arrays. New experiences overwrite the oldest ones using an index pointer. This made memory management faster and more stable.

Another optimization was storing raw NumPy values in the buffer instead of immediately converting them to tensors. Since not every stored experience is used for training, this avoids unnecessary computation.

---

### Training on random batches

The model is trained using random batches sampled from the replay buffer. This improves learning stability because the network does not learn only from consecutive, strongly correlated states.

For example, without random sampling, the model could train on many almost identical frames of the lander falling straight down. Random batches reduce this problem and make the learning process more balanced.

---

### Learning network and target network

Two neural networks were used:

- the learning network,
- the target network.

The learning network is updated during training, while the target network is updated less frequently. This prevents the model from constantly chasing a target that changes immediately after every update.

This improvement had one of the biggest positive effects on training stability and final agent performance.

---

### Observation normalization

Input observations were normalized to a similar numerical range. This prevents larger input values, such as velocity, from having an unfairly strong influence compared to smaller values, such as angle.

Normalization made learning more stable and helped the neural network process the environment state more effectively.

---

## Training and Evaluation Logs

During development, report-generation functions were implemented. They automatically save training plots, model metadata, hyperparameters, and selected evaluation results into Markdown report files.

Some selected training and evaluation logs are included below.

---