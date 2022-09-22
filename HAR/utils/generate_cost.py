# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 14:33:12 2022

@author: mrzhe
"""

import math
import align_utils
from pm4py.objects.log import log as log_implementation
from pm4py.algo.conformance.alignments.variants import dijkstra_less_memory

STD_TAU_COST = 0 # hidden transition cost

def generate_cost_model(net, epsilon):
    cost_model = {}
    for tt in net.transitions:
        if tt.label is None:
            cost_model[tt] = STD_TAU_COST  # add cost of hidden transitions
        else:
            cost_model[tt] = - math.log(epsilon) # threshold 1.61
    return cost_model

def generate_prob_model(net):
    prob_model = {}
    for tt in net.transitions:
        # cost_model[tt] = - math.log(1)+ (- math.log(0.4)) # threshold 1.61
        prob_model[tt] = 1
    return prob_model

def generate_cost_sync(trace_net, model_net, cost_log, cost_model, epsilon): 
    cost_sync = dict()
    for t_trace in trace_net.transitions:
        for t_model in model_net.transitions:
            if t_trace.label == t_model.label:
                # print(t_trace.name, "cost model:",cost_model[t_model],"cost log:", cost_log[t_trace])
                # cost_sync[(t_trace, t_model)] = min(cost_model[t_model],cost_log[t_trace])
                cost_sync[(t_trace, t_model)] =  cost_log[t_trace] + math.log(epsilon)  # threshold
    return cost_sync

# probability of sync net for visulization
def generate_prob_sync(trace_net, model_net, prob_log):
    prob_sync = dict()
    for t_trace in trace_net.transitions:
        for t_model in model_net.transitions:
            if t_trace.label == t_model.label:
                # print(t_trace.name, "cost model:",cost_model[t_model],"cost log:", cost_log[t_trace])
                # cost_sync[(t_trace, t_model)] = min(cost_model[t_model],cost_log[t_trace])
                prob_sync[(t_trace, t_model)] =  prob_log[t_trace]  # threshold
    return prob_sync

def generate_normal_cost(sync_net):
    normal_cost = {}
    for i in sync_net.transitions:
        if "None" in str(i):
            normal_cost[i]=0 # move on model on hidden transition
        elif ">>" in str(i):
            normal_cost[i]=10000 # move on log or move on model in normal transitions
        else:
            normal_cost[i]=0 # synchronous transitions
    return normal_cost

def generate_prob(alignment,df):
    r_prob = 1
    m=0
    path= []
    for t in alignment:
        if t[0] != ">>":
            r_prob = r_prob * df.loc[m,t[0]]
            m += 1
            path.append(t[0])
    return r_prob, path

# assign fitness to traces


def get_best_worst_cost(petri_net, initial_marking, final_marking, parameters=None):
    """
    Gets the best worst cost of an alignment

    Parameters
    -----------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    -----------
    best_worst_cost
        Best worst cost of alignment
    """
    if parameters is None:
        parameters = {}
    trace = log_implementation.Trace()

    best_worst = dijkstra_less_memory.apply(trace, petri_net, initial_marking, final_marking, parameters=parameters)

    if best_worst['cost'] > 0:
        return best_worst['cost'] // align_utils.STD_MODEL_LOG_MOVE_COST
    return 0



def generate_fitness(align, log, petri_net, initial_marking, final_marking):
    if align is not None:
        best_worst_cost = get_best_worst_cost(petri_net, initial_marking, final_marking)
        unfitness_upper_part = align['normal_cost'] // align_utils.STD_MODEL_LOG_MOVE_COST
        if unfitness_upper_part == 0:
            fitness = 1
        elif (len(log.index) + best_worst_cost) > 0:
            fitness = 1 - (
                    (align['normal_cost'] // align_utils.STD_MODEL_LOG_MOVE_COST) / (len(log.index) + best_worst_cost))
        else:
            fitness = 0
    return fitness