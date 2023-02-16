"""
This file contains some useful functions for EEG analysis

Author: Laura Bock Paulsen
"""

import numpy as np

def add_trigger(trigger_list, trigger_code, sample):
    """
    Adds a trigger to the EEG data
    args:
        trigger_list(np.array): The current trigger list
        trigger_code(int): The trigger code for the new trigger
        sample(int): The sample number for the new trigger event
    """
    new_trigger_list = np.append(trigger_list, [[sample, 0, trigger_code]])

    return new_trigger_list.reshape(-1, 3)
