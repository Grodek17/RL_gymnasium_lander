from constants import MAX_X, MAX_Y, MAX_VELOCITY_X, MAX_VELOCITY_Y, MAX_ANGLE, MAX_ANGULAR_VELOCITY

def normalise_observation(obs):
    obs[0] = obs[0]/MAX_X
    obs[1] = obs[1]/MAX_Y
    obs[2] = obs[2]/MAX_VELOCITY_X
    obs[3] = obs[3]/MAX_VELOCITY_Y
    obs[4] = obs[4]/MAX_ANGLE
    obs[5] = obs[5]/MAX_ANGULAR_VELOCITY
    return obs