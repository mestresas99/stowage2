import sys
import os
import time
import numpy as np


class Node():
    def __init__(self,parent=None, position=None):
        self.containers = {} #list of all containers and their positions
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

global position_all_containers #global variable for the position of all the containers
position_all_containers = {}
def readInputs(): #read files for each of the inputs
    if len(sys.argv)!=5:
        return len(sys.argv),len(sys.argv)
    path = sys.argv[1]
    map_file = sys.argv[2]
    containers_file = sys.argv[3]
    global heur #variable of the type of heuristic
    heur = sys.argv[4]
    path_map = path + map_file
    path_containers = path + containers_file
    global boat_map #variable that includes the map of the boat
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
    global next_cell_available #cells that mus be occupied next taking into account gravity
    global next_cell_available_original #first cell that is available i each of the stacks of the boat (auxiliary variable for recalculating next_cell_available)
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
    next_cell_available_original = next_cell_available.copy()
    return boat_map,containers


def load(container, position): #creates the children state that will come from applying a load operation to the parent
    position_dict = position_all_containers.copy()
    position_dict.update({container[0]:position}) #changes the position of a container
    return position_dict

def isPossible(container,position): #sees if a position is correct (refrigerated and non refrigerated containers)
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

def unload(container,port): #creates the child states that come from an unloading operation from the parent
    position_dict = position_all_containers.copy()
    pos = -1 - port
    position_dict[container[0]] = [pos,pos] #-1 for port 0, -2 for port 1 and -3 for port 2
    return position_dict

def hasArrived(node,container): #sees it the container is already in the destination port
    if node.containers[container[0]][0] == -1 - int(container[2]):
        return True
    else:
        return False

def allArrived(node,containers):
    for container in containers:
        if not hasArrived(node,container):
            return False
    return True

def sail(node, port): #changes the port of a node (not used in the final implementation)
    node.position = port

def isLoaded(container): #checks if a container is already in he boat or not
    if position_all_containers[container[0]][0]<0:
        return False
    else:
        return True

def samePort(container,position_boat): #check if we are in the same port that an unloaded container, or if we have sailed to another location
    position = position_all_containers[container[0]]
    if position[0] == (-1 - position_boat):
        return True
    else:
        return False

def heuristic1(node,containers): #checks the number of operations left for arriving to the goal (relaxing the restriction of loading contianers that are on different port than when we are and supposing that we must arrive to port 2 at the end)
    num_to_load = 0
    for c in node.containers.keys():
        for cont in containers:
            if cont[0] == c:
                if node.containers[c][0] < 0 and node.containers[c][0]!=-1 - int(cont[2]):
                    num_to_load+=1
    sails_to_finish = 2 - node.position
    return (2 *2000*num_to_load) + 2000*sails_to_finish


def heuristic2(node, containers):
    num_to_load = 0
    unloads_correct = 0
    unloads_incorrect = 0
    for c in node.containers.keys():
        for cont in containers:
            if cont[0] == c:
                if node.containers[c][0] < 0 and node.containers[c][0]!=-1 - int(cont[2]):
                    num_to_load+=1
                elif node.containers[c][0]>=0 and cont[2]==node.position:
                    unloads_correct +=1
                elif node.containers[c][0]>=0 and cont[2]!=node.position:
                    unloads_incorrect +=1
    return (2 *10000* num_to_load) + unloads_correct + 100*unloads_incorrect 

def bubble_sort(open): #function for sorting the vector of nodes
    n = len(open)

    for i in range(n-1):
        for j in range(0, n-i-1):
            if open[j].f > open[j+1].f:
                open[j], open[j+1] = open[j+1], open[j]
    return open

def generateChildren(current_node,containers,expanded_nodes): #calls the load and unload methods and create all the children for a given parent
    children = []
    for container in containers:
        if (not isLoaded(container)) and (not hasArrived(current_node,container)) and (samePort(container,current_node.position)):
            for i in range(len(next_cell_available)):
                if next_cell_available[i]!= -1 and isPossible(container,[int(next_cell_available[i]),i]):
                    node = Node(parent=current_node,position=current_node.position)
                    node.containers = load(container,[int(next_cell_available[i]),i])
                    node.g = 10 + next_cell_available[i]
                    children.append(node)
                    expanded_nodes = expanded_nodes + 1
        else:
            if position_all_containers[container[0]][0] == next_cell_available[position_all_containers[container[0]][1]] + 1:
                node = Node(parent=current_node,position=current_node.position)
                node.containers = unload(container,current_node.position)           
                node.g = 15 + 2*next_cell_available[position_all_containers[container[0]][0]]
                children.append(node)
                expanded_nodes = expanded_nodes + 1
    for i in range(3):
        if i!= current_node.position:
            node = Node(parent=current_node, position=i) #works the same way as sail function
            node.containers = position_all_containers.copy()
            node.g = 3500 * np.abs(i-current_node.position)
            children.append(node)
            expanded_nodes = expanded_nodes + 1
            
    return children, expanded_nodes

def recalculate_next_cell_available(containers): #recalculate the positions where we can add the containers
    min_pos = next_cell_available_original.copy()
    for i in containers.keys():
        if containers[i][0]>=0:
            if containers[i][0] - 1 < min_pos[containers[i][1]]:
                min_pos[containers[i][1]] = containers[i][0] - 1
    for j in range(len(min_pos)):
        next_cell_available[j] = min_pos[j]

        
def astar(start, containers, map, position_all_containers): #a-star implementation
    start_node = Node(position=start)
    expanded_nodes = 0
    actions = []
    start_node.containers = position_all_containers.copy()
    open = []
    close = []
    path_solution = []
    exit = False
    #add start node to open list
    open.append(start_node)

    while len(open)>0 and not exit:
        current_node = open.pop(0)
        close.append(current_node)
        position_all_containers.update(current_node.containers.copy())
        recalculate_next_cell_available(current_node.containers)
        #check if it is goal
        if allArrived(current_node,containers): 
            exit = True
            last_node= current_node
        else:
            children, expanded_nodes = generateChildren(current_node,containers,expanded_nodes)
            for child in children: #see if the children are in the closed vector, in the open vector and change the cost if they are already in the open vector
                found = False
                # Create the f and h values
                if heur == "heuristic1": #calculate the heuristic
                    child.h = heuristic1(child,containers) #call to the heuristic
                else:
                    child.h = heuristic2(child,containers) #space for the second heuristic
                child.f = child.g + child.h
                for closed_node in close: #check if it is in closed_node
                    if child.containers == closed_node.containers and child.position == closed_node.position:
                        found=True
                if found == False:
                    for open_node in open: #check if it is in the open node
                        if child.containers == open_node.containers and child.position == open_node.position:
                            found = True
                            if child.f < open_node.f:
                                open.remove(open_node)   
                                open.append(child)
                if found == False:
                    open.append(child) 
            open = bubble_sort(open) #sort the open vector from less cost to more

    if exit: #close should be change with path (to be fixed)
        while last_node.parent:
            path_solution.append(last_node)
            last_node = last_node.parent
        path_solution.append(start_node)
        solution = path_solution
    else:
        solution = None
    return solution,expanded_nodes

def main():
    boat_map_2d,containers = readInputs()
    start = 0 #home port
    start_time = time.time()
    path,expanded_nodes = astar(start, containers, boat_map_2d,position_all_containers)
    end_time = time.time()
    t = (end_time - start_time )*1000
    map_file=sys.argv[2]
    containers_file = sys.argv[3]
    heuristic_file= sys.argv[4]
    map_name,_ = os.path.splitext(map_file)
    containers_name,_ =os.path.splitext(containers_file)
    heuristic_name,_ =os.path.splitext(heuristic_file)
    file_name1 = "ASTAR-tests/output-" + map_name + "-" + containers_name + "-" + heuristic_name + ".output"
    with open(file_name1,'wb') as f: #include the output file
        for i in range(len(path)-1):
            if i<len(path)-1:
                j = len(path)-1 -i
                containers_first = path[j].containers
                containers_after_action = path[j-1].containers
                position_first = path[j].position
                position_after_action = path[j-1].position
                for conts in containers_first.keys():
                    if containers_first[conts][0] != containers_after_action[conts][0]:
                        if containers_first[conts][0]>=0:
                            action = "unload"
                            cont_name = conts
                        else:
                            action="load"
                            cont_name = conts
                            posi = containers_after_action[conts]
                if position_first!=position_after_action:
                    action="sail"
            if action == "sail":
                solution = str(i+1) + "." +  str(action) + "(Destination port:" + str(position_after_action) + ")" + "\n"
                f.write(bytes(solution, encoding = 'utf-8'))
            elif action=="load":
                for c in containers:
                    if c[0] == cont_name:
                        container_type = c[1]
                        cont_dest = c[2]
                solution = str(i+1) + "." +str(action) + "(Container ID:" +str(cont_name) + " Container type:"+ str(container_type)+ " Container destination:" + str(cont_dest) + " Desired position:"  + str(posi) + " Port of the ship:" + str(position_first) + ")" + "\n"
                f.write(bytes(solution, encoding = 'utf-8'))
            else:
                for c in containers:
                    if c[0] == cont_name:
                        container_type = c[1]
                        cont_dest = c[2]
                solution = str(i+1) + "." +str(action) + "(Container ID:" +str(cont_name) + " Container type:"+ str(container_type) + " Container destination:" + str(cont_dest) + " Port of the ship:" + str(position_first) + ")" + "\n"
                f.write(bytes(solution, encoding = 'utf-8'))

    file_name2 = "ASTAR-tests/output-" + map_name + "-" + containers_name + "-" + heuristic_name + ".stat"
    with open(file_name2,'wb') as f: #include the output file
        tim = "Overall time: " + str(t) + "\n"
        f.write(bytes(tim, encoding = 'utf-8'))
        total_cost = 0
        for node in path:
            total_cost += node.g
        totalC = "Overall cost: " + str(total_cost) + "\n"
        f.write(bytes(totalC, encoding = 'utf-8'))
        path_len = "Path length: " + str(len(path)) + "\n"
        f.write(bytes(path_len, encoding = 'utf-8'))
        exp_n = "Expanded nodes: " + str(expanded_nodes) + "\n"
        f.write(bytes(exp_n, encoding = 'utf-8'))


if __name__ == '__main__':
    bool = main()

