from merson.get_information import get_task_nodes
from copy import deepcopy
import json
import re

template = {
    "tasks":{},
    "events":{},
    "gateways":{},
    "sequenceFlows":[]
}

final_template = {
    "tasks":[],
    "events":[],
    "gateways":[],
    "pools":[],
    "sequenceFlows":[],
    "messageFlows":[]
}

""" extract unique list of tasks from generated mermaid.js model """
def get_elements(content,elements):
    content = content.splitlines()
    counter = 0
    for c in content:
        flow = {}
        nodes = c.split("-->")
        for i in range(len(nodes)):
            n = nodes[i]
            if ":" in n:
                node_id = n.split(":")[0].strip()
                node_type =  n.split(":")[1].strip()
                if "|" in node_id:
                    node_id = re.search(r'(\d+$)',node_id).group()
                flow["id"] = "sf{}".format(counter)
                if i == 0:
                    flow["sourceRef"] = node_id
                elif i == 1:
                    flow["targetRef"] = node_id

                if "task" in node_type:
                    label = get_task_nodes(n,r'\((.*?)\)')
                    if label:
                        elements["tasks"][node_id] = label
                elif "event" in node_type:
                    elements["events"][node_id] = node_type
                elif "gateway" in node_type:
                    elements["gateways"][node_id] = node_type
        if flow:
            elements["sequenceFlows"].append(flow)
            counter = counter + 1
    return elements

""" return the last id in the model """
def get_max_keys(elements):
    elements.pop('sequenceFlows', None)
    ids = []
    for e in elements:
        key = list(elements[e].keys())
        ids.extend(key)
    ids = [eval(i) for i in ids]
    maxi = max(ids) + 1
    return maxi

""" adjust the list of unique elements according to the sap schema """
def sort_elements(elements,final):
    for e in elements:
        for t in elements[e]:
            if e == "tasks":
                task = {'id': t,'name':elements[e][t],'type':'User'}
                final["tasks"].append(task)
            elif e == "events":
                if "start" in elements[e][t]:
                    event = {'id': t,'name':'start','type':'StartNoneEvent'}
                elif "end" in elements[e][t]:
                    event = {'id': t,'name':'end','type':'EndNoneEvent'}
                final["events"].append(event)
            elif e == "gateways":
                if "exclusive" in elements[e][t]:
                    gateway = {'id': t,'type':'Exclusive'}
                elif "parallel" in elements[e][t]:
                    gateway = {'id': t,'type':'Parallel'}
                else:
                    gateway = {'id': t,'type':'UNDEFINED'}
                final["gateways"].append(gateway)
    final["sequenceFlows"] = elements["sequenceFlows"]
    final = json.dumps(final, indent = 4)
    return final

""" convert mermaid.js model into bpmn.json """
def mermaid_to_json(generated):
    all_nodes = get_elements(generated,deepcopy(template))
    print(all_nodes)
    converted = sort_elements(all_nodes,deepcopy(final_template))
    return converted

def transform_nodes(model):
    nodes = {}
    for etype in model:
        for e in model[etype]:
            elem_id = e["id"]
            if etype == "tasks":
                task_label = e["name"]
                node = "{}:{}:({})".format(elem_id,"task",task_label)
                nodes[elem_id] = node
            elif etype == "events":
                event_type = e["type"]
                if "start" in event_type.lower():
                    node_type = "startevent"
                    event_label = "start event"
                elif "end" in event_type.lower():
                    node_type = "endevent"
                    event_label = "end event"
                else:
                    continue
                node = "{}:{}:(({}))".format(elem_id,node_type,event_label)
                nodes[elem_id] = node
            elif etype == "gateways":
                gateway_type = e["type"].lower()
                if gateway_type == "exclusive" or "exclusive" in gateway_type:
                    node_type = "exclusivegateway"
                    gate_label = "x"
                elif gateway_type == "parallel" or "parallel" in gateway_type:
                    node_type = "parallelgateway"
                    gate_label = "AND"
                elif gateway_type == "inclusive" or "inclusive" in gateway_type:
                    node_type = "inclusivegateway"
                    gate_label = "O"
                else:
                    continue
                node = "{}:{}:{{{}}}".format(elem_id,node_type,gate_label)
                nodes[elem_id] = node
    print(nodes)
    return nodes

def define_structure(model,nodes):
    tupels = []
    flow = model["sequenceFlows"]
    for f in flow:
        source = f["sourceRef"]
        target = f["targetRef"]
        tupel = "{} --> {}".format(nodes[source],nodes[target])
        tupels.append(tupel)
    mermaid = "\n".join(tupels)
    mermaid = "graph LR\n" + mermaid
    return mermaid

def json_to_mermaid(json_data):
    nodes = transform_nodes(json_data)
    new_model = define_structure(json_data,nodes)
    return new_model

