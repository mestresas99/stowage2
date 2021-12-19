import sys
import os
import time
import numpy as np


class Node():
    def __init__(self, position=None):
        self.containers = {}
        self.map = []
        self.fCost = 0
        self.position = position #postion can be 0,1,2 depends on the port we are
        # 0 stands for the home port
        # 1 stands for the first port
        # 2 stands for the second port
        self.f = 0
        self.g = 0
        self.h = 0
    
    def __eq__(self, other):
        return self.position == other.position

global position_all_containers
position_all_containers={}
def readInputs():
    if len(sys.argv)!=5:
        return len(sys.argv),len(sys.argv)
    path = sys.argv[1]
    map_file = sys.argv[2]
    containers_file = sys.argv[3]
    global heur
    heur = sys.argv[4]
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
                if boat_map[access][i]!='X' and obtained==False:
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
    for cont in containers:
        position_all_containers.update({cont[0]:[-1,-1]})
    global boat_map_first_len
    boat_map_first_len = len(boat_map)
    global boat_map_cols
    boat_map_cols = len(boat_map[0])
    return boat_map,containers


def load(container, position):
    position_dict = position_all_containers.deepcopy()
    position_dict.update({container[0]:position})
    return position_dict

def isPossible(container,position):
    if container[1] =="R":
        if boat_map[int(position[0])][position[1]] == "E":
            return True
        else:
            return False
    else:
        if boat_map[int(position[0])][position[1]] == "E":
            return True
        elif boat_map[int(position[0])][position[1]] == "N":
            return True
        else:
            return False

def hasArrived(container):
    if container[0] in arrived:
        return True
    else:
        return False

arrived = []
def unload(container,port):
    position_dict = position_all_containers.deepcopy()
    position = position_dict[container[0]]
    pos = -1 - position
    position_dict[container[0]] = [pos,pos]
    if container[2] == port:
        arrived.append(container[0])
    return position_dict

def sail(node, port):
    node.position = port

def isLoaded(container):
    if position_all_containers[container[0]][0]<0:
        return False
    else:
        return True

def samePort(container,position_boat):
    position = position_all_containers[container[0]]
    if position[0] == (-1 - position_boat):
        return True
    else:
        return False

def heuristic1(node,containers):
    num_to_load = 0
    unloads = 0
    for c in position_all_containers.keys():
        for cont in containers:
            if cont == c:
                if position_all_containers[c][0] < 0 and position_all_containers[c][0]!=-1 - cont[2]:
                    num_to_load+=1
                if position_all_containers[c][0]>=0:
                    unloads +=1
    
    sails_to_finish = 2 - node.position
    
    return (2 * num_to_load) + unloads + sails_to_finish


#def heuristic2():

def bubble_sort(open):
    n = len(open)

    for i in range(n-1):
        for j in range(0, n-i-1):
            if open[j].f > open[j+1].f:
                open[j], open[j+1] = open[j+1], open[j]
    return open

def generateChildren(current_node,containers):
    children = []
    for container in containers:
        if (not isLoaded(container)) and (not hasArrived(container)) and (samePort(container,current_node.position)):
            for i in range(len(next_cell_available)):
                node = Node(current_node.position)
                if next_cell_available[i]!= -1 and isPossible(container,[int(next_cell_available[i]),i]):
                    print('load')
                    node.containers = load(container,[int(next_cell_available[i]),i])
                    node.g = 10 + next_cell_available[i]
                    children.append(node)
        else:
            if position_all_containers[container[0]][0] == next_cell_available[position_all_containers[container[0]][1]] + 1:
                node = Node(current_node.position)
                print('unload')
                node.containers = unload(container,current_node.position)           
                node.g = 15 + 2*next_cell_available[position_all_containers[container[0]][0]]
                children.append(node)
    for i in range(3):
        if i!= current_node.position:
            print('sail')
            node = Node(i) #works the same way as sail function
            node.g = 3500 * np.abs(i-current_node.position)
            children.append(node)
            
    return children

def recalculate_next_cell_available(containers):
    min_pos =1000*np.ones(boat_map_cols)
    for i in containers.keys():
        if containers[i][0]>=0:
            if containers[i][0] - 1 < min_pos[containers[i][1]]:
                print(containers[i][1])
                print(containers[i][0] -1)
                min_pos[containers[i][1]] = containers[i][0] - 1
    for j in range(len(min_pos)):
        if min_pos[j]!=1000:
            next_cell_available[j] = min_pos[j]
    print(min_pos)
        
def astar(start, containers, map):
    start_node = Node(start)
    start_node.map = map
    open = []
    close = []
    path = []
    exit = False
    #add start node to open list
    open.append(start_node)

    while len(open)>0 and not exit:
        current_node = open.pop(0)
        close.append(current_node)
        position_all_containers = current_node.containers.deepcopy()
        recalculate_next_cell_available(current_node.containers)
        print("next cell av loop" + str(next_cell_available))
        #check if it is goal
        if (len(arrived) == len(containers)): 
            exit = True
        
        children = generateChildren(current_node,containers)
        # #generate childrens
        # childrens = []
        # for container in containers:
        #     if (not isLoaded(container)) and (not hasArrived(container)) and (samePort(container,current_node.position)):
        #         for i in range(len(next_cell_available)):
        #             node = Node(current_node,current_node.position)
        #             path.append(current_node)
        #             if next_cell_available[i]!= -1 and isPossible(container,[next_cell_available[i],i]):
        #                 #node.operator = ["load",container,[next_cell_available[i],i]]
        #                 node.g = 10 + next_cell_available[i]
        #                 childrens.append(node)
        #     else: #container is in the ship loaded
        #         if position_all_containers[container[0]][0] == next_cell_available[position_all_containers[container[0]][1]] + 1:
        #             node = Node(current_node,current_node.position)
        #             path.append(current_node)
        #             for i in range(3):
        #                 if i== current_node.position:
        #                     #node.operator = ["unload",container,current_node.position]
        #                     node.g = 15 + 2*next_cell_available[i]
        #                     childrens.append(node)
        # for i in range(3):
        #     if i!= current_node.position:
        #         node = Node(current_node,current_node.position)
        #         path.append(current_node)
        #         #node.operator = ["sail",i]
        #         node.g = 3500 * np.abs(i-current_node.position)
        #         childrens.append(node)
        
        for child in children:
            found = False
            for closed_node in close:
                if child.containers == closed_node.containers and child.position == closed_node.position:
                    found=True
            if found == False:
                for open_node in open:
                    if child.containers == open_node.containers and child.position == open_node.position:
                        found = True
                        if child.f < open_node.f:
                            del open_node   
                            open.append(child)
            if found == False:
                open.append(child) 
            
            # Create the f, g, and h values
            if heur == "heuristic1":
                child.h = heuristic1(child,containers) #call to the heuristic
            else:
                pass
            child.f = child.g + child.h
        open = bubble_sort(open)
        if len(open)>0:
            print(open[1].containers)
            

    if exit:
        solution = close
    else:
        solution = None

    return open, solution

                        

def main():
    boat_map_2d,containers = readInputs()
    print(boat_map_2d)
    print(containers) 
    start = 0 #home port
    start_time = time.time()
    open, path = astar(start, containers, boat_map_2d)
    end_time = time.time()
    t = (end_time - start_time )*1000
    print(t)
    print(open)
    print(path)

if __name__ == '__main__':
    bool = main()

