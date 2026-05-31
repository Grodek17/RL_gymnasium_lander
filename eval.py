import gymnasium
import torch
import random
from helpers import normalise_observation

env = gymnasium.make("LunarLander-v3", continuous=False, gravity=-10.0, enable_wind=False, wind_power=15.0, turbulence_power=0.5, render_mode="human")


def reportResults(evaluation_steps, rewards, model_filename, random_baseline=False):
    ''' ASKING TO SAVE '''
    while True:
        print("save evaluation stats? [y/n]")
        save = input()
        if save == "y":
            break
        elif save == "n":
            return


    ''' MARKDOWN UPDATE '''
    print("Write title of report section in markdown file: ")
    title = input()
    print("please write note about this specific model/evaluation: ")
    note = input()
    with open("report_data.md", "a", encoding="utf-8") as file:
        file.write(f"#=== EVALUATION: {title} ===\n\n")
        file.write(f"random actions (random baseline)?: {random_baseline}\n")
        file.write(f"network file name: {model_filename} \n")
        file.write(f"note: {note}\n")
        file.write("---------------------\n")
        file.write(f"Number of evaluation episodes: {evaluation_steps}\n")

        file.write("## Rewards\n")

        for reward in rewards:
            file.write(f"{reward:.2f}\n")
        file.write("#================\n\n")



#action is chosen always by network
def action_choosing(x, trained_model):

    with torch.no_grad():               
        qvalues = trained_model(x)
        action = torch.argmax(qvalues).item()

    return action


#main loop of training in the enviroment
def evaluation(evaluation_steps, trained_model, model_filename, random_baseline):
    trained_model.eval()
    rewards = []

    for episode in range(evaluation_steps):
        obs, info = env.reset()             #starting state
        obs = normalise_observation(obs)
        episode_ended = False
        total_reward = 0

        while not episode_ended:
            if random_baseline == True:
                action = random.randint(0,3)
            elif random_baseline == False:
                action = action_choosing(torch.tensor(obs), trained_model)

            next_obs, reward, terminated, truncated, info = env.step(action)    #take the next step
            next_obs = normalise_observation(next_obs)
            episode_ended = terminated or truncated                                  #check if crashed or truncuated
            obs = next_obs                                                          #next step becomes initial step
            total_reward += reward                                                  #sum rewards     
            

            if(terminated or truncated):
                print("Episode: ", episode, " | reward: ", total_reward, " |")  
                rewards.append(total_reward)


    env.close()  
    print("rewards get by model: ", rewards)
    

    reportResults(evaluation_steps, rewards, model_filename, random_baseline)