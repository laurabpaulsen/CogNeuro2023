# Mouse tracking experiment
This directory is an example of how to structure and run an EEG experiment using PsychoPy. This can be used as inspiration for your own project. 

### Organisation
```
├── data                                <- Directory for saving behavioural data from experiment
├── experimental_details               
│   └── experimental_info.csv           <- csv file containing information for each trial (e.g., stimuli and condition)
├── stimuli                             <- Directory with stimuli files
│   ├── ost.png
│   ├── ost_gul.png
│   ├── ost_rod.png
│   └── ...       
├── README.md                           <- The top-level README for this project.  
├── run_experiment.py                   <- Script for running the experiment
└── triggers.py                         <- Script for sending triggers to the EEG system (imported into run_experiment.py)
```
