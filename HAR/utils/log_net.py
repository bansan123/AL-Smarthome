# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 13:02:12 2022

@author: mrzhe
"""

from pm4py.objects.petri.petrinet import PetriNet, Marking


# import pandas as pd
# import numpy as np
import math
import visualize_prob as prob_visualizer                                     
from pm4py.visualization.petrinet import visualizer as pn_visualizer    


def add_arc_from_to(fr, to, net, weight=1):
    """
    Adds an arc from a specific element to another element in some net. Assumes from and to are in the net!

    Parameters
    ----------
    fr: transition/place from
    to:  transition/place to
    net: net to use
    weight: weight associated to the arc

    Returns
    -------
    None
    """
    a = PetriNet.Arc(fr, to, weight)
    net.arcs.add(a)
    fr.out_arcs.add(a)
    to.in_arcs.add(a)

    return a

# df = pd.DataFrame(np.array([[0.8, 0.1, 0.1], [0.2, 0.7, 0.1], [0.1, 0.2, 0.7]]), columns=['a', 'b', 'c'])

def generate_log_net(df, epsilon):
    """
    Generate log petri net given the probabilistic df
    
    
    Parameters
    ------
    df
        Probabilistic dataframe of event log
        
    Returns
    --------
    
    net
        petri net
    im 
        initial marking
    fm
        final marking
    cost_function
        cost of each transition
    prob_function
        probability of each transition
    
    """
    trace_net = PetriNet("trace")
    
    place_map = {0: PetriNet.Place('p_0')}
    trace_net.places.add(place_map[0])
    
    cost_function = {}
    prob_function = {}
    df[df<0.001] = 0
    for index, row in df.iterrows():
        row = row/row.sum()
        place_map[index+1] = PetriNet.Place('p_' + str(index))
        trace_net.places.add(place_map[index+1])
        for t in df.columns:
            if row[t] != 0:
                tt = PetriNet.Transition(t + "_" + str(index),t)
                cost_function[tt] = - math.log(row[t]) + (-math.log(epsilon)) # no threshold  
                prob_function[tt] =row[t]
                trace_net.transitions.add(tt)
                
                add_arc_from_to(place_map[index], tt, trace_net)
                add_arc_from_to(tt, place_map[index + 1], trace_net)
                
    return trace_net, Marking({place_map[0]: 1}), Marking({place_map[len(df)]: 1}), cost_function, prob_function


def visualize_log_net(df):
    net, im, fm, _, prob_log = generate_log_net(df)
    decorations_log = {}
    for t1 in prob_log:
        decorations_log[t1] = {"prob":prob_log[t1]}
    gviz_s = prob_visualizer.apply(net, im, fm, decorations = decorations_log)
    pn_visualizer.view(gviz_s)

def visualize_sync_net(syncnet, im, fm, prob_function):
    decorations_sync = {}
    for t1 in prob_function:
        decorations_sync[t1] = {"prob":prob_function[t1]}
    gviz_s = prob_visualizer.apply(syncnet, im, fm, decorations = decorations_sync)
    pn_visualizer.view(gviz_s)
    
    
# net, initial_marking, final_marking, cost_log, prob_log = generate_log_net(df)

# from pm4py.visualization.petrinet import visualizer as pn_visualizer
# gviz = pn_visualizer.apply(net, initial_marking, final_marking)
# pn_visualizer.view(gviz)


# import visualize_prob as prob_visualizer

# decorations_log = {}
# for t1 in prob_log:
#     decorations_log[t1] = {"prob":prob_log[t1]}

    
    
# gviz_s = prob_visualizer.apply(net, initial_marking, final_marking, decorations= decorations_log)
# pn_visualizer.view(gviz_s)

# for i, t in enumerate(df.columns):
#     tt = PetriNet.Transition(t)
#     trace_net.transitions.add(tt)
#     place_map[i] = PetriNet.Place('p_' + str(t))
#     trace_net.places.add(place_map[t])
#     add_arc_from_to(place_map[t], tt, trace_net)
#     add_arc_from_to(t, place_map[i + 1], net)
    