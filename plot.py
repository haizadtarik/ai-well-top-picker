from toppicker import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np

def well_splitter(dataframe, groupby_column):
    grouped = dataframe.groupby(groupby_column)
    
    # Create empty lists
    wells_as_dfs = []
    wells_wellnames = []

    #Split up the data by well
    for well, data in grouped:
        wells_as_dfs.append(data)
        wells_wellnames.append(well)

    return wells_as_dfs, wells_wellnames

def create_plot(wellname, dataframe, curves_to_plot, depth_curve, top_curves=[]):
    # Count the number of tracks we need
    num_tracks = len(curves_to_plot)
    
    top_color = ['#F4D03F', '#F5B041','#DC7633','#6E2C00', '#1B4F72','#2E86C1', '#AED6F1', '#A569BD', '#196F3D', 'red','black', 'blue', 'green', 'yellow']
             
    # Setup the figure and axes
    fig, ax = plt.subplots(nrows=1, ncols=num_tracks, figsize=(num_tracks*2, 10))
    
    # Create a super title for the entire plot
    fig.suptitle(wellname, fontsize=20, y=1.05)
    
   # Loop through each curve in curves_to_plot and create a track with that data
    for i, curve in enumerate(curves_to_plot):
        if curve in top_curves:
            cmap_top = colors.ListedColormap(top_color[0:dataframe[curve].max()], 'indexed')
            
            cluster=np.repeat(np.expand_dims(dataframe[curve].values,1), 100, 1)
            im=ax[i].imshow(cluster, interpolation='none', cmap=cmap_top, aspect='auto',vmin=dataframe[curve].min(),vmax=dataframe[curve].max(), extent=[0,20, depth_curve.max(), depth_curve.min()])
        else:
            ax[i].plot(dataframe[curve], depth_curve)

        
        # Setup a few plot cosmetics
        ax[i].set_title(curve, fontsize=14, fontweight='bold')
        ax[i].grid(which='major', color='lightgrey', linestyle='-')
        
        # We want to pass in the deepest depth first, so we are displaying the data 
        # from shallow to deep
        ax[i].set_ylim(depth_curve.max(), depth_curve.min())

        # Only set the y-label for the first track. Hide it for the rest
        if i == 0:
            ax[i].set_ylabel('DEPTH (m)', fontsize=18, fontweight='bold')
        else:
            plt.setp(ax[i].get_yticklabels(), visible = False)
    fig.savefig('result.png')

df = pd.read_csv('test.csv')
del df['Unnamed: 0']
data = df.iloc[:50000]

X = data[['GR','DT','RES']]
trainer = Trainer()
trainer.load('model/top_picker_model')
msg, yhat = trainer.predict(X)
data['prediction'] = yhat
gp_tops = df['FORMATION'].unique()
gp_tops_map = {gp_tops[i]: i for i in range(0, len(gp_tops))}
data['Actual'] = data['FORMATION'].map(gp_tops_map)
data['Predicted'] = data['prediction'].map(gp_tops_map)

dfs_wells, wellnames = well_splitter(data, 'well_name')
curves_to_plot = ["DT", "RES", "GR",  'Actual', 'Predicted']
top_curve=['Actual', 'Predicted']
well = 0
create_plot(wellnames[well], 
        dfs_wells[well], 
        curves_to_plot, 
        dfs_wells[well]['DEPTH'], 
        top_curve)