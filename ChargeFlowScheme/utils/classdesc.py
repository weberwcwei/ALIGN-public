
class primitive:
    def __init__(self, primitive_name, block_name, parent, connections, ismodule):
        self.primitive_name = primitive_name
        self.block_name = block_name
        self.parent = parent
        self.connections = connections # 'connections' is a dictionary
        self.ismodule = ismodule

    def __str__(self):
        return "primitive: {}\nblock: {}\nparent: {}\n connections: {}\nismodule: {}\n" \
                .format(self.primitive_name, self.block_name, self.parent, self.connections, self.ismodule)

class module:
    def __init__(self, name, portlist, netlist, id):
        self.name = name
        self.portlist = portlist
        self.netlist = netlist
        self.id = id

    def __str__(self):
        str_to_print = "Module name: " + self.name + "\nmodule id: " + str(self.id) + "\nportlist: " + str(self.portlist) + "\n"
        for item in self.netlist:
            str_to_print = str_to_print + str(item)
        # str_to_print = str_to_print + str(self.netset) + "\n"
        return str_to_print


class device:
    def __init__(self, name, type, deviceid):        #line contains [dev name] [nodelist] [dev type]
        self.name = name
        self.type = type
        self.id = deviceid

class transistor(device):
    def __init__(self, name, type, deviceid, nodelist):
        super().__init__(name, type, deviceid)
        self.connections = dict()
        self.connections["D"] = nodelist[0]
        self.connections["G"] = nodelist[1]
        self.connections["S"] = nodelist[2]
        self.connections["B"] = nodelist[3]

    def __str__(self):
        return "name: {}\ntype: {}\nid: {}\nconnections: {}\n" \
                .format(self.name, self.type, self.id, self.connections)


class passive(device):
    def __init__(self, name, type, deviceid, nodelist):
        super().__init__(name, type, deviceid)
        self.connections = dict()
        self.connections["PLUS"] = nodelist[0]
        self.connections["MINUS"] = nodelist[1]

    def __str__(self):
        return "name: {}\ntype: {}\nid: {}\nconnections: {}\n" \
                .format(self.name, self.type, self.id, self.connections)

class net:
    def __init__(self, name, isundertest, netid):
        self.name = name
        self.isundertest = isundertest
        self.connections = list()
        self.branchcurrents = list()
        self.id = netid
    def __str__(self):
        return "name: {}\nisundertest: {}\nnet id: {}\nconnections: {}\nbranches: {}\n" \
                .format(self.name, self.isundertest, self.id, self.connections, self.branchcurrents)

class subcircuit:
    def __init__(self, name, portlist, netlist, id):
        self.name = name
        self.portlist = portlist
        self.netlist = netlist
        self.id = id
    def __str__(self):
        str_to_print = "Subcircuit name: " + self.name + "\nsubcircuit id: " + str(self.id) + "\nportlist: " + str(self.portlist) + "\n"
        for item in self.netlist:
            str_to_print = str_to_print + str(item)
        # str_to_print = str_to_print + str(self.netset) + "\n"
        return str_to_print
