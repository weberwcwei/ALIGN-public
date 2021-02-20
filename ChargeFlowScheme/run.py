import logging
import argparse
import timeit
import os
import pandas as pd


parser = argparse.ArgumentParser(description = 'This functions generates ML \
                                 models from performance constraints.')
parser.add_argument('-design', '--design', type = str, metavar = '',
                    required = True, help = 'Netlist under test')

args = parser.parse_args()
logging.basicConfig(filename = 'run.log', filemode = 'w', level = logging.INFO,
                    format = '%(name)s - %(levelname)s - %(message)s')

WORK_DIR = os.getcwd()

def extract_module_info(line):
    line_splited = line.split()
    module_name = line_splited[1]
    node_list = list()
    logging.info("Extracting module:{}" .format(module_name))
    for i in range(3, len(line_splited) - 1, 1):
        node_list.append(line_splited[i].strip(','))
    logging.info("Node list of module - {}: {}" .format(module_name, node_list))



def main():
    logging.info('Starting ChargeFlow...')
    # spice_file = args.design + ".sp"
    verilog_file = args.design + ".v"
    cf_const_file = args.design + ".cfconst"

    device_type_set = set() # stores device and subcircuits types in the circuit

    if not os.path.exists(WORK_DIR + "/test_example/" + verilog_file):
        logging.critical("{} not found. Quitting ChargeFlow scheme." .format(verilog_file))

    with open(WORK_DIR + "/test_example/" + verilog_file) as fverilog:
        for line in fverilog:
            if line.strip().startswith("//"):
                continue
            elif line.strip().startswith("module"):
                if line.split()[1] == args.design:
                    pass
                elif line.split()[1] == "global_power;":
                    pass
                else:
                    extract_module_info(line)

    #                 # print(line)
    #                 revised_netlist = revised_netlist + line
    #                 device_type_set.add(line.split()[1])
    #                 # print(device_type_set)
    #                 for line in finput:
    #                     if line.startswith("ends" or ".ends"):
    #                         break
    #                     else:
    #                         revised_netlist = revised_netlist + line
    #                         pass
    #             else:
    #                 for num,item in enumerate(line.split()):
    #                     if item in device_type_set:
    #                         dev_desc = " ".join(line.split()[:num+1])
    #                         others = " ".join(line.split()[num+1:])
    #                         device_list.append(device(dev_desc,nodes_under_test,node_list,device_type_set))
    #                         dev_desc = dev_desc.replace('(',' ').replace(')',' ')
    #                         for nodes in device_list[-1].nodelist:
    #                             if nodes.name.isnumeric():
    #                                 dev_desc = re.sub(r'(?<=\s)'+nodes.name+" "," "+nodes.alias+" ",dev_desc)
    #                         line = dev_desc + ' ' + others + '\n'
    #                         break
    #         revised_netlist = revised_netlist + line
    #     fnew.write(revised_netlist)
    # return device_list, node_list


if __name__ == "__main__":
    main()
