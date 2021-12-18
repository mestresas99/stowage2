import sys
import os
import time


def readInputs():
    if len(sys.argv)!=4:
        return len(sys.argv),len(sys.argv)
    path = sys.argv[1]
    map_file = sys.argv[2]
    containers_file = sys.argv[3]
    path_map = path + map_file
    path_containers = path + containers_file
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


cells_occupied ={}
def load(container, boat_map_2d):
    found = False
    if container[1]=='R':
        for i in range(len(boat_map_2d)):
            for j in range(len(boat_map_2d[i])):
                if boat_map_2d[i][j] == 'E' and found== False:
                    if container[0] not in cells_occupied.keys() and [i,j] not in cells_occupied.values():
                        cells_occupied.update({container[0]:[i,j]})
                        found = True

    elif container[1]=='S':
        for i in range(len(boat_map_2d)):
            for j in range(len(boat_map_2d[i])):
                if boat_map_2d[i][j]!='X' and found== False:
                    if container[0] not in cells_occupied.keys() and [i,j] not in cells_occupied.values():
                        cells_occupied.update({container[0]:[i,j]})
                        found = True
    
    print(cells_occupied)

arrived = []
def unload(container, node):
    for cont in cells_occupied.keys():
        if cont == container[0]:
            del cells_occupied[cont]
            if cont[2] == node.position:
                arrived.append(cont[0])

def sail(node, position):
    node.position = position

def isLoaded(container):
    for cont in cells_occupied.keys():
        if cont == container[0]:
            return True
    return False

def astar(start, end, containers, map):
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
        current_index = 0
        for index, item in enumerate(open):
            if item.f < current_node.f:
                current_node = item
                current_index = index
        #pop current off open list, add to closed list        
        open.pop(current_index)
        close.append(current_node)

        #check if it is goal
        if (len(cells_occupied)==0 and (len(arrived) == len(containers))): 
            exit = True
        
        #generate childrens
        childrens = []
        for container in containers:
            if ( not isLoaded(container)):
                node = Node(current_node,current_node.position)
                node.operator = ["load",container,[i,j]]
                childrens.append(node)
            else: #container is in the ship loaded
                node = Node(current_node,current_node.position)
                #TODO: CHECK PORT TO UNLOAD
                node.operator = ["unload",container]
                childrens.append(node)
        for i in range(3):
            if i!= current_node.position:
                node = Node(current_node,current_node.position)
                node.operator = ["sail",i]
                childrens.append(node)
        
        for child in childrens:
            if child not in open:
                if child not in close:
                    open.append(child)
            
            # Create the f, g, and h values
            child.g = current_node.g + 1 #TODO modify the cost in terms of operation
            child.h = heuristic1() #call to the heuristic
            child.f = child.g + child.h
            
            else:
                for open_node in open:
                    if child == open_node and child.g > open_node.g:
                        continue 



def main():
    boat_map_2d,containers = readInputs()
    print(boat_map_2d)
    print(containers) 
    #for i in containers:               
        #load(i, boat_map_2d)
    start = 0 #home port
    end = 3 #final port
    #start_time = time()
    #path = astar(start, end, containers, boat_map_2d)
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
