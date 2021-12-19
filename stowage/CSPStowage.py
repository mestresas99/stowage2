from constraint import *
import sys
import os

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

def checkConstraintPorts(cells1, cells2,boat_map):
    if (cells1%boat_map)==(cells2%boat_map):
        if cells2<cells1:
            return False
    return True

def checkConstraintGravity(*cells): 
    index=[0]*boat_map_cols
    sumcol=[0]*boat_map_cols
    for cells1 in cells:
        column=cells1%boat_map_first_len
        index[column]+=1
        sumcol[column]+=cells1
    for column_num in range(boat_map_cols):
        i = index[column_num]
        sumMax=0
        for val in range(len(values)):
            access = len(values) - 1 - val
            if values[access]%boat_map_first_len == column_num and i>0:
                i -= 1
                sumMax = sumMax + values[access]
        if sumMax!=sumcol[column_num]:
            return False
    return True

def main():
    problem = Problem()
    boat_map_2d,containers = readInputs()
    num_x = 0
    for i in range(boat_map_first_len):
        for j in range(boat_map_cols):
            if boat_map_2d[i][j] == "X":
                num_x += 1
    if len(containers) < (boat_map_first_len*boat_map_cols - num_x):
        global values
        for container in containers:
            cells_occupied =[]
            for i in range(len(boat_map_2d)):
                for j in range(len(boat_map_2d[i])):
                    if container[1]=='R' and boat_map_2d[i][j] == 'E':
                        cells_occupied.append(j+i*len(boat_map_2d))
                    elif container[1]=='S' and boat_map_2d[i][j]!='X':
                        cells_occupied.append(j+i*len(boat_map_2d))
                        values = cells_occupied
            if len(cells_occupied)!=0:
                problem.addVariable(container[0],cells_occupied)
            else:
                return False
        for cont1 in containers:
            for cont2 in containers:
                if(cont1[0] != cont2[0]):
                    problem.addConstraint(AllDifferentConstraint(), (cont1[0], cont2[0])) #constraint to avoid containers to have the same cell
                if cont1[2] < cont2[2]:
                    problem.addConstraint(lambda cells1, cells2: checkConstraintPorts(cells1,cells2,len(boat_map_2d)), (cont1[0],cont2[0])) #constraint fo check destination ports and assign cells in order
        problem.addConstraint(checkConstraintGravity,[id[0] for id in containers])
        Solutions=problem.getSolutions()
        #print(problem.getSolutions())
        for index in range(len(Solutions)):
            for element in Solutions[index]:
                i = int(Solutions[index][element]/len(boat_map_2d))
                j = Solutions[index][element]%len(boat_map_2d)
                Solutions[index][element] = (j,i)
        map_file=sys.argv[2]
        containers_file = sys.argv[3]
        map_name,_ = os.path.splitext(map_file)
        containers_name,_ =os.path.splitext(containers_file)
        file_name = "outputs/output-" + map_name + "-" + containers_name + ".output"
        with open(file_name,'wb') as f: #include the output file
            if len(Solutions)!=0:
                for solution in Solutions:
                    solution = str(solution) + "\n"
                    f.write(bytes(solution, encoding = 'utf-8'))
            else:
                solution = "There is not a solution that fulfills this problem: not satisfiable"
                f.write(bytes(solution, encoding = 'utf-8'))
    else:
        map_file=sys.argv[2]
        containers_file = sys.argv[3]
        map_name,_ = os.path.splitext(map_file)
        containers_name,_ =os.path.splitext(containers_file)
        file_name = "outputs/output-" + map_name + "-" + containers_name + ".output"
        with open(file_name,'wb') as f: #include the output file
            solution = "No solution for this problem: more containers than spaces in the boat"
            f.write(bytes(solution, encoding = 'utf-8'))


if __name__ == '__main__':
    bool = main()
    if bool == False:
        map_file=sys.argv[2]
        containers_file = sys.argv[3]
        map_name,_ = os.path.splitext(map_file)
        containers_name,_ =os.path.splitext(containers_file)
        file_name = "outputs/output-" + map_name + "-" + containers_name + ".output"
        with open(file_name,'wb') as f: #include the output file
            solution = "Not enough refrigerated cells for the containers: no solutions for this problem"
            f.write(bytes(solution, encoding = 'utf-8'))
