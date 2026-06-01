import gymnasium
from gymnasium.wrappers import RecordVideo
from moviepy import VideoFileClip
import torch
import random
from helpers import normalise_observation
from NeuralNetworkClass import NeuralNetwork
from datetime import datetime

def convert_mp4_to_gif(mp4_path, gif_path):
    clip = VideoFileClip(mp4_path)
    clip = clip.resized(width=600)  
    clip.write_gif(gif_path, fps=15)
    clip.close()

def reportResults(evaluation_steps, rewards, trained_model_path, random_baseline, saved_data, gif_path=False ):
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
    time = datetime.now().strftime("%Y:%m:%d:%H:%M")
    
    with open("report_data.md", "a", encoding="utf-8") as file:
        file.write(f"# EVALUATION: {title} ===  \n\n  ")
        file.write(f"Evaluation date: {time}  \n\n  ")
        file.write(f"random actions (random baseline)?: {random_baseline}  \n  ")
        file.write(f"network file name: {trained_model_path}  \n  ")
        file.write(f"Number of evaluation episodes: {evaluation_steps}  \n  ")
        file.write(f"note: {note}  \n\n  ")

        if gif_path != False:
            file.write(f"## Evaluation video:  \n  ")
            file.write(f"![Evaluation GIF]({gif_path})  \n\n"  )      


        file.write("=== network details ===\n")
        file.write(f"Input size: {saved_data['input_size']}\n")
        file.write(f"First hidden layer size: {saved_data['first_layer_size']}\n")
        file.write(f"Second hidden layer: {saved_data['second_layer_size']}\n")
        file.write(f"activation function: {saved_data['activation']}\n")
        file.write(f"output size: {saved_data['output_size']}\n")
        file.write(f"network 'graph': {saved_data['input_size']} -> {saved_data['first_layer_size']} -> {saved_data['activation']} -> {saved_data['second_layer_size']} -> {saved_data['activation']} -> {saved_data['output_size']}\n\n")

        file.write(f"=== training details ===\n")
        file.write(f"Number of training episodes: {saved_data['num_of_training_eps']}\n")
        file.write(f"Buffer size: {saved_data['buffer_size']}\n")
        file.write(f"Batch size: {saved_data['batch_size']}\n")
        file.write(f"Target network updated each {saved_data['network_update_each']} steps \n \n")

        file.write(f"=== Q learning parameters ===\n")
        file.write(f"Gamma: {saved_data['gamma']}\n")
        file.write(f"Initial epsilon: {saved_data['initial_epsilon']} \n")
        file.write(f"Epsilon lowered each episode by {saved_data['epsilon_subtract']}\n")
        file.write(f"Minimal epsilon: {saved_data['min_epsilon']} \n")
        file.write(f"Learning rate: {saved_data['learning_rate']}\n\n")

        file.write("## Rewards\n")

        for reward in rewards:
            file.write(f"{reward:.2f}\n")
        file.write("\n\n")



#action is chosen always by network
def action_choosing(x, trained_model):

    with torch.no_grad():               
        qvalues = trained_model(x)
        action = torch.argmax(qvalues).item()

    return action


#main loop of training in the enviroment
def evaluation(evaluation_steps, trained_model_path, random_baseline=False, record_video=False):
    env = gymnasium.make("LunarLander-v3", continuous=False, gravity=-10.0, enable_wind=False, wind_power=15.0, turbulence_power=0.5, 
                         render_mode="rgb_array" if record_video else "human")
    
    # recording video setup:
    if record_video:
        print("Evaluated network path: ", trained_model_path, " please give name of video: ")
        name = input()
        env = RecordVideo(
            env,
            video_folder="videos",
            name_prefix=name,
            episode_trigger=lambda episode_id: episode_id == 0,
            video_length=5000
        )

    #reading the model from file & all the data:
    data = torch.load(trained_model_path, map_location="cpu", weights_only=False)

    trained_model = NeuralNetwork(data["input_size"], data["first_layer_size"], data["second_layer_size"], data["output_size"], data["activation"], data["saved_weights_torch"])
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
                print("Episode: ", episode, " | reward: ", round(total_reward, 2), " |")  
                rewards.append(round(float(total_reward), 2))


    env.close()  
    print("rewards get by model: ", rewards)
    
    if RecordVideo:
        convert_mp4_to_gif("videos/" + name + "-episode-0.mp4", "videos/" + name + ".gif")

    reportResults(evaluation_steps, rewards, trained_model_path, random_baseline, data,
                   gif_path="videos/" + name + ".gif" if RecordVideo else False)