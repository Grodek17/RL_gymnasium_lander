import numpy as np
import torch
from constants import DEBUG



#class for storing states of the enviroment, for training the neural network
class ExperienceBuffer():
    def __init__(self, max_size):
        self.buffermaxsize = max_size
        self.current_size = 0
        self.writing_index = 0
        self.observations = np.zeros((max_size, 8), dtype=np.float32)
        self.actions = np.zeros((max_size,), dtype=np.int64)
        self.next_observations = np.zeros((max_size, 8), dtype=np.float32)
        self.rewards = np.zeros((max_size,), dtype=np.float32)
        self.dones = np.zeros((max_size,), dtype=np.int64)


    #arguments passed as arrays and int's, not always used in batch -> no need to transform (improved time efficiency)
    def add(self, observation, action, next_observation, reward, done):
        #adding the data
        self.observations[self.writing_index] = observation
        self.actions[self.writing_index] = action
        self.next_observations[self.writing_index] = next_observation
        self.rewards[self.writing_index] = reward
        self.dones[self.writing_index] = done

        #updating the size of buffer
        if self.current_size < self.buffermaxsize:
            self.current_size += 1
        
        #updating the writing index
        if self.writing_index < (self.buffermaxsize - 1):
            self.writing_index += 1
        else:
            self.writing_index = 0


    #provides batch of separate vectors of each attribute, used in later computing
    def giveRandomBatch(self, batch_size):
        if DEBUG:
            print("selecting batch_size random entries from list")

        if self.current_size < (batch_size * 2):
            raise ValueError("Buffer not full, cannot give random batch", self.current_size, "<- buffer lenght | full size (-5) -> ", (self.buffermaxsize - 2))

        batch_obs = np.zeros((batch_size, 8), dtype=np.float32)
        batch_act = np.zeros((batch_size,), dtype=np.int64)
        batch_next = np.zeros((batch_size, 8), dtype=np.float32)
        batch_rew = np.zeros((batch_size,), dtype=np.float32)
        batch_dones = np.zeros((batch_size,), dtype=np.int64)

        #get array of random numbers from (0;current_size), then fill arrays with theese indices
        indices = np.random.randint(0, self.current_size, size=batch_size)
        batch_obs = self.observations[indices]
        batch_act = self.actions[indices]
        batch_next = self.next_observations[indices]
        batch_rew = self.rewards[indices]
        batch_dones = self.dones[indices]
            

        #turning into tensors 
        packed_observations = torch.from_numpy(batch_obs)
        packed_actions = torch.from_numpy(batch_act)
        packed_nexts = torch.from_numpy(batch_next)
        packed_reward = torch.from_numpy(batch_rew)
        packed_dones = torch.from_numpy(batch_dones)

        if DEBUG:
            print("=== Random Batch Print ===")
            print("packed_obs: ", packed_observations)
            print(packed_observations.shape, packed_observations.dtype)
            print("packed_actions: ", packed_actions)
            print(packed_actions.shape, packed_actions.dtype)
            print("packed_nexts: ", packed_nexts)
            print(packed_nexts.shape, packed_nexts.dtype)
            print("packed_reward: ", packed_reward)
            print(packed_reward.shape, packed_reward.dtype)
            print("packed_dones: ", packed_dones)
            print(packed_dones.shape, packed_dones.dtype)
            print("============================= END ====================")
            #raise ValueError("debug new converion")
            
        
        return packed_observations, packed_actions, packed_nexts, packed_reward, packed_dones

    
    def printBuffer(self):
        print("Class parameters: ")
        print("max size: ", self.buffermaxsize, " current_size: ", self.current_size, " writing index: ", self.writing_index)
        print("=== PRINT OF WHOLE BUFFER STARTED ===")
        print(self.observations)
        print(self.actions)
        print(self.next_observations)
        print(self.rewards)
        print(self.dones)
