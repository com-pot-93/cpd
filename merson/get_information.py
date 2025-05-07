import re
#import mermaid as md
#from mermaid.graph import Graph
import os
import json


""" check if all keys were generated """
def add_keys(model):
    req_keys = ["tasks","events","gateways","pools","sequenceFlows","messageFlows"]
    keys = list(model.keys())
    for k in req_keys:
        if k not in keys:
            print(k)
            print("------------add key function was used")
            model[k] = []
    return model


""" clean model after generation """
def clean_model(gen):
    first = gen.find('{')
    last = gen.rfind('}') + 1
    json_str = gen[first:last]
    try:
        json_obj = json.loads(json_str)
        json_obj = add_keys(json_obj)
    except json.JSONDecodeError as e:
        json_obj = {"error":"Not a valid json"}
    return json_obj


""" extract text between () from string """
def get_task_nodes(t,reg_ex):
    try:
        label = re.findall(reg_ex, t)
        if label:
            return label[0]
    except:
        return None

""" extract unique list of tasks from generated mermaid.js model """
def extract_mermaid_tasks(content):
    content = content.splitlines()
    elements = []
    try:
        for c in content:
            tasks = c.split("-->")
            for t in tasks:
                if "task" in t:
                    label = get_task_nodes(t,r'\((.*?)\)')
                    if label:
                        elements.append(label)
    except:
        pass
    if elements:
        elements = list(dict.fromkeys(elements))
    return elements

#""" check if mermaid model is a valid mermaid.js """
#def validate_mermaid(mermaid,file_name="temp"):
#    status = 0
#    file = "{}.svg".format(file_name)
#    graph: Graph = Graph('example-flowchart',mermaid)
#    graphe: md.Mermaid = md.Mermaid(graph)
#    graphe.to_svg(file)
#    f = open(file, "r")
#    if "invalid encoded code" in f.read():
#        status = 0
#    else:
#        status = 1
#    os.remove(file)
#    return status
#
""" check if mermaid model corresponds to custom predefined rules """
def validate_custom_format(content,details=0):
    status = 1
    elements = {"tasks":{},"events":{}}
    errors = []
    content = content.splitlines()
    counter = 0
    for j in range(len(content)):
        c = content[j]
        if c and "graph" not in c and "flowchart" not in c:
            nodes = c.split("-->")
            #if len(nodes) > 2:
            #    errors.append("There are more nodes than allowed nodes in line #{}".format(j))
            if len(nodes) <= 1:
                errors.append("There are less nodes than allowed in line #{}".format(j))
            else:
                for i in range(len(nodes)):
                    n = nodes[i]
                    node_parts = n.split(":")
                    if node_parts:
                        if len(node_parts) <= 1:
                            errors.append("There is a node than violate predefined structure in line #{}".format(j))
                        else:
                            #print(n)
                            if re.search(r"^(\S+):(\S+):(.*$)", n):
                                #print(node_parts)
                                node_id = node_parts[0].strip()
                                if "|" in node_id:
                                    try:
                                        node_id = re.search(r'(\d+$)',node_id).group()
                                    except:
                                        errors.append("There is a node than violate predefined structure in line #{}".format(j))
                                node_type = node_parts[1].strip()
                                node_text = node_parts[2].strip()
                                if "--" in node_text:
                                    node_text = node_text.split("--")[0].strip()
                                if "task" in node_type:
                                    label = get_task_nodes(n,r'\((.*?)\)$')
                                    if label:
                                        if node_id in elements["tasks"]:
                                            if re.search('[a-zA-Z]',label):
                                                if label != elements["tasks"][node_id]:
                                                    errors.append("Node #{} has multiple labels".format(node_id))
                                            else:
                                                errors.append("Node #{} has no label".format(node_id))
                                        else:
                                            if re.search(r'[(|)]+',label):
                                                errors.append("Node #{} violates the predefined rules".format(node_id))
                                            else:
                                                elements["tasks"][node_id] = label
                                    #else:
                                    #    errors.append("Node #{} has no label".format(node_id))
                                elif "event" in node_type:
                                    if "start" not in node_type and "end" not in node_type:
                                        errors.append("Type of node #{} is not coresponding to the predefined format.".format(node_id))
                                    else:
                                        if "start" in node_type:
                                            elements["events"][node_id] = node_type
                                        if not re.match(r'(^\(\(.*?\)\)$)',node_text):
                                           errors.append("The syntax of node #{} is not coresponding to the predefined format.".format(node_id))
                                elif "gateway" in node_type:
                                    if "exclusive" not in node_type and "parallel" not in node_type:
                                        errors.append("Type of node #{} is not coresponding to the predefined format.".format(node_id))
                                    else:
                                      if node_text:
                                          if not re.match(r'(^\{.*?\}$)',node_text):
                                             errors.append("The syntax of node #{} is not coresponding to the predefined format.".format(node_id))
                                else:
                                    errors.append("Nodetype {} is not defined".format(node_type))
    if len(elements["events"]) > 1:
        errors.append("There are multiple start events in the model.".format(node_type))
    if len(errors) > 0:
        status = 0
    return status, errors

""" return sorted list of tasks and their amount """
def get_task_info(tasks):
    info = {}
    info["tasks"] = sorted(tasks)
    info["number"] = len(tasks)
    return json.dumps(info, indent=4)

""" compare the list of two tasks and return tasks which are identical and different """
""" only for simple and fast inspection: exact matching (no semantic similarity) """
def compare_tasks(tasks1,tasks2):
#TODOs: add similar
    output = {}
    output["ident"] = []
    output["not_ident1"] = []
    output["not_ident2"] = []
    list1 = [t.replace(" ","").lower() for t in tasks1]
    list2 = [t.replace(" ","").lower() for t in tasks2]
    for i,l in enumerate(list1):
        if l in list2:
            output["ident"].append(tasks1[i])
        else:
            output["not_ident1"].append(tasks1[i])
    for i,l in enumerate(list2):
        if l not in list1:
            output["not_ident2"].append(tasks2[i])
    return output


