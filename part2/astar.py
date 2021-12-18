import sys
import os
import time
import numpy as np


def readInputs():
    if len(sys.argv)!=4:
        return len(sys.argv),len(sys.argv)
    path = sys.argv[1]
    map_file = sys.argv[2]
    containers_file = sys.argv[3]
    path_map = path + map_file
    path_containers = path + containers_file
    global boat_map
    boat_map = []
    containers =[]
    with open(path_map, 'r') as fmap:
        file_lines =fmap.readlines()
        counter = 1
        for i in file_lines:
            if counter!=len(file_lines):
                i = i[:-1]
            boat_map.append(i.split(" "))
            counter += 1
        fmap.close()
    global next_cell_available
    next_cell_available = np.zeros(len(boat_map[0]))
    for i in range(len(boat_map[0])):
        obtained = False
        for val in range(len(boat_map)):
                access = len(boat_map) - 1 - val
                if boat_map[access,i]!="X" and obtained==False:
                    obtained=True
                    next_cell_available[i] = access
    with open(path_containers, 'r') as fcontainers:
        file_lines =fcontainers.readlines()
        counter = 1
        for i in file_lines:
            if counter!=len(file_lines):
                i = i[:-1]
            containers.append(i.split(" "))
            counter += 1
        fcontainers.close()
    global boat_map_first_len
    boat_map_first_len = len(boat_map)
    global boat_map_cols
    boat_map_cols = len(boat_map[0])
    return boat_map,containers

def heuristic1():
    




def heuristic2():




position_all_containers ={}
def load(container, position):
    position_all_containers.update({container[0]:position})
    next_cell_available[position[1]] = next_cell_available[position[1]] - 1
    print(position_all_containers)

def isPossible(container,position):
    if container[1] =="R":
        if boat_map[position[0]][position[1]] == "E":
            return True
        else:
            return False
    else:
        if boat_map[position[0]][position[1]] == "E":
            return True
        elif boat_map[position[0]][position[1]] == "N":
            return True
        else:
            return False

def hasArrived(container):
    if container[0] in arrived:
        return True
    else:
        return False

arrived = []
def unload(container, position):
    for cont in position_all_containers.keys():
        if cont == container[0]:
            position = position_all_containers[cont]
            next_cell_available[position[1]] = position[0]
            pos = -1 - position
            position_all_containers[cont] = [pos,pos]
            if cont[2] == position:
                arrived.append(cont[0])

def sail(node, port):
    node.position = port

def isLoaded(container):
    for cont in position_all_containers.keys():
        if cont == container[0]:
            return True
    return False

def samePort(container,position_boat):
    position = position_all_containers[container[0]]
    if position[0] == (-1 - position_boat):
        return True
    else:
        return False

def astar(start, containers, map):
    start_node = Node(None, start)
    start_node.containers = containers
    start_node.map = map
    open = []
    close = []
    exit = False
    #add start node to open list
    open.append(start_node)

    while len(open)>0 or not exit:

        #get the current node
        current_node = open[0]
        if current_node.operator[0] == "load":
            load(current_node.operator[1],current_node.operator[2])
        elif current_node.operator[0] == "unload":
            unload(current_node.operator[1],current_node.operator[2])
        else:
            sail(current_node, current_node.operator[1])
            
        current_index = 0
        for index, item in enumerate(open):
            if item.f < current_node.f:
                current_node = item
                current_index = index
        #pop current off open list, add to closed list        
        open.pop(current_index)
        close.append(current_node)

        #check if it is goal
        if (len(position_all_containers)==0 and (len(arrived) == len(containers))): 
            exit = True
        
        #generate childrens
        childrens = []
        for container in containers:
            if (not isLoaded(container)) and (not hasArrived(container)) and (samePort(container,current_node.position)):
                for i in range(len(next_cell_available)):
                    node = Node(current_node,current_node.position)
                    if next_cell_available[i]!= -1 and isPossible(container,[next_cell_available[i],i]):
                        node.operator = ["load",container,[next_cell_available[i],i]]
                        node.g = 10 + next_cell_available[i]
                        childrens.append(node)
            else: #container is in the ship loaded
                if position_all_containers[container][0] == next_cell_available[position_all_containers[container][1]] + 1:
                    node = Node(current_node,current_node.position)
                    for i in range(3):
                        if i== current_node.position:
                            node.operator = ["unload",container,current_node.position]
                            node.g = 15 + 2*next_cell_available[i]
                            childrens.append(node)
        for i in range(3):
            if i!= current_node.position:
                node = Node(current_node,current_node.position)
                node.operator = ["sail",i]
                node.g = 3500 * np.abs(i-current_node.position)
                childrens.append(node)
        
        for child in childrens:
            if child not in open:
                if child not in close:
                    #TODO: INSERT IN ORDER TO OPEN LIST
                    open.append(child)
            
            # Create the f, g, and h values
            child.h = heuristic1() #call to the heuristic
            child.f = child.g + child.h
            
            if child in open:
                for open_node in open:
                    if child.f > current_node.f:

                    if child == open_node and child.g > open_node.g:
                        continue 



def main():
    boat_map_2d,containers = readInputs()
    print(boat_map_2d)
    print(containers) 
    #for i in containers:               
        #load(i, boat_map_2d)
    start = 0 #home port
    #start_time = time()
    #path = astar(start, containers, boat_map_2d)
    #end_time = time()
    #t = (end_time - start_time )*1000
    #print(t)
    #print(path)
    for container in containers:
        load(container, boat_map_2d)

if __name__ == '__main__':
    bool = main()

class Node():
    def __init__(self, parent=None, position=None):
        self.containers = []
        self.map = []
        self.operator = []
        self.fCost = 0
        self.parent = parent
        self.position = position #postion can be 0,1,2 depends on the port we are
        # 0 stands for the home port
        # 1 stands for the first port
        # 2 stands for the second port
        self.f = 0
        self.g = 0
        self.h = 0
    
    def __eq__(self, other):
        return self.position == other.position
