# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 14:34:18 2022

@author: mrzhe
"""
from pm4py.objects.petri.synchronous_product import construct_cost_aware
from synchronous_product import construct_prob_aware
import state_equation_a_star as prob_a_star
import log_net as log
import generate_cost
from pm4py.visualization.petrinet import visualizer as pn_visualizer


def generate_log_net(df,epsilon):
    """
    Generate event log given a probabilistic df.
    Parameters
    -----------
    df
        Probabilistic dataframe of event log.

    Returns
    -----------
    log_net
        Event log petri net with net, initial marking, final marking, and df.
    decorations_log
        Decorations for visualizing the event log. 
    """
    log_net = {}
    net, im, fm, cost_log, prob_log = log.generate_log_net(df,epsilon)
    log_net["event"] = df
    log_net["net"] = net
    log_net["im"] = im
    log_net["fm"] = fm
    log_net["cost_log"] = cost_log
    decorations_log = {}
    for t1 in prob_log:
        decorations_log[t1] = {"prob":prob_log[t1]}
    return log_net, decorations_log, prob_log
    

def apply(df,model_net, epsilon):
    """
    Given the event log dataframe and model net, then do probabilistic conformance checking.
    
    Parameters
    ----------
    df
        Probabilistic dataframe of event log.
        
    Returns
    ----------
    most_prob_result
        Return the conformance checking result with detailed alignment, fitness, probability and so on.
    
    """
    log_net, decorations_log, prob_log = generate_log_net(df,epsilon)
    cost_model = generate_cost.generate_cost_model(model_net["net"], epsilon)
    prob_model = generate_cost.generate_prob_model(model_net["net"])
    cost_sync = generate_cost.generate_cost_sync(log_net["net"],model_net["net"],log_net["cost_log"],cost_model,epsilon)
    prob_sync = generate_cost.generate_prob_sync(log_net["net"],model_net["net"],prob_log)
    
    sync_net, im_s, fm_s, cost_function = construct_cost_aware(log_net["net"], log_net["im"], log_net["fm"], model_net["net"], model_net["im"], model_net["fm"],'>>', log_net["cost_log"], cost_model, cost_sync)
    
    sync_net_1, im_s_1, fm_s_1, prob_function = construct_prob_aware(log_net["net"], log_net["im"], log_net["fm"], model_net["net"], model_net["im"], model_net["fm"],'>>',prob_log, prob_model, prob_sync)
    
    #visualize prob sync net
    # log.visualize_sync_net(sync_net_1, im_s_1, fm_s_1, prob_function)
    
    # visualize sync net
    # gviz_model = pn_visualizer.apply(sync_net, im_s, fm_s)
    # pn_visualizer.view(gviz_model)
    
    normal_cost = generate_cost.generate_normal_cost(sync_net)
    most_prob_result = prob_a_star.apply_sync_prod(sync_net, im_s, fm_s, cost_function, normal_cost, ">>")
    most_prob_result["probability"], most_prob_result["path"] = generate_cost.generate_prob(most_prob_result["alignment"],log_net["event"])
    # most_prob_result["probability"]=r_prob
    
    # (align, log, petri_net, initial_marking, final_marking)
    most_prob_result["fitness"] = generate_cost.generate_fitness(most_prob_result,log_net["event"],model_net["net"], model_net["im"], model_net["fm"])
    return most_prob_result


