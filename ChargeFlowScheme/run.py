#!/scratch/anaconda/bin/python3

import logging
import argparse
import timeit
import os
import pandas as pd
import itertools
import math
import re
import numpy as np
import csv

from utils.classdesc import primitive, module, transistor, passive, net, subcircuit

parser = argparse.ArgumentParser(description = 'This functions generates ML \
                                 models from performance constraints.')
parser.add_argument('-design', '--design', type = str, metavar = '',
                    required = True, help = 'Netlist under test')

args = parser.parse_args()
logging.basicConfig(filename = 'run.log', filemode = 'w', level = logging.INFO,
                    format = '%(name)s - %(levelname)s - %(message)s')

WORK_DIR = os.getcwd()
DEVICE_TYPE_SET = {
    'resistor', 'capacitor', 'nmos_rf',
    'pch', 'vsource', 'isource',
    'vcvs', 'nfet', 'pfet',
    'rmres', 'nfet_b', 'pfet_b',
    }
# TRANSISTOR_PORTS = {0: "d", 1: "g", 2: "s", 3: "b"}
TRANSISTOR_PORTS = {0: "1", 1: "2", 2: "3"} # ignoring gate and body connections for now
# 1:d , 2:g, 3:s, 4:b
PASSIVE_PORTS = {0: "1", 1: "2"}

def extract_primitive(module_name, line, ismodule):
    line_splited = line.split()
    primitive_name = line_splited[0]
    block_name = line_splited[1]
    connections = dict()
    # logging.info("Extracting module:{}" .format(block_name))
    # print(line)
    for i in range(3, len(line_splited) - 1, 1):
        # print(line_splited[i])
        pin_name, net_name = line_splited[i].split('(')
        pin_name = pin_name.strip('.')
        net_name = net_name.strip('),')
        connections[net_name] = pin_name
    temp_primitive = primitive(primitive_name, block_name, module_name, connections, ismodule)
    # logging.info("Details:\n{}" .format(temp_primitive))
    return temp_primitive

def check_if_module(primitive_name, modulelist):
    # primitive_name = line.split()[0]
    for module in modulelist:
        if module.name == primitive_name:
            return True
        else:
            pass
    return False

# def prepare_cfconst(design, modulelist):
#     temp_dict = dict()
#     tc_directory = "/testcase_" + design + "/"
#
#     for module in modulelist:
#         if module.name == args.design:
#             os.chdir(WORK_DIR + tc_directory)
#             with open(design + ".cfconst", 'w') as fcfconst:
#                 for net in module.netlist:
#                     if net.isundertest:
#                         temp_list = list()
#                         for connection in net.connections:
#                                 if not connection[1] == "B":
#                                     temp_list.append(connection[0] + "/" + connection[1])
#                         temp_dict[net.name] = temp_list
#                 print(temp_dict)
                # for item in temp_dict:
                #     line = ""
                #     pin_combos = list(itertools.combinations(temp_dict[item], 2))
                #     # print(pin_combos)
                #     for pin_combo in list(pin_combos):
                #         fcfconst.write(item + "    " + pin_combo[0] + "    " + pin_combo[1] + "\n")
                #         module.branch_under_test.append([item, pin_combo[0], pin_combo[1]])
    # return modulelist


def extract_spice_netlist(design):
    spicefile = design + ".sp"
    tc_directory = "/testcase_" + design + "/"
    subcircuit_list = list()
    subcircuit_id = 0
    logging.info("Extracting spice file: {}" .format(spicefile))

    if not os.path.exists(WORK_DIR + tc_directory + spicefile):
        logging.critical("{} not found. Quitting ChargeFlow scheme." .format(spicefile))
        exit()

    with open(WORK_DIR + tc_directory + "nets_under_test.txt", "r") as fnode:
        for line in fnode:
            nets_under_test = line.strip().split()

    with open(WORK_DIR + tc_directory + spicefile, "r") as fspice:
        for line in fspice:
            if not line.strip().startswith("//"):
                if line.strip().startswith(".subckt"):
                    netlist = list()
                    netid = 0
                    list_from_line = line.strip().split()
                    subcircuit_name = list_from_line[1]
                    portlist = list_from_line[2:]
                    for line in fspice:
                        if line.strip().startswith("m"):
                            list_from_line = line.strip().split()
                            # temp_list_with_drain_source = [list_from_line[1], list_from_line[3]]
                            temp_list_with_drain_source = list_from_line[1:4]
                            device_name = list_from_line[0]
                            for i, pin in enumerate(temp_list_with_drain_source): # ignoring body terminal for now
                                get_netid = pin_is_in_the_list(pin, netlist)
                                if get_netid is not None:
                                    netlist[get_netid].connections.append([device_name, TRANSISTOR_PORTS[i]])
                                    # flag = 0
                                    # for connection in netlist[get_netid].connections: # The script will just take one connection for each net device combination
                                    #     if device_name == connection[0]:
                                    #         flag = 1
                                    #         break
                                    #     else:
                                    #         pass
                                    # if flag == 0:
                                    #     netlist[get_netid].connections.append([device_name, TRANSISTOR_PORTS[i]])
                                    # else:
                                    #     pass
                                else:
                                    isundertest = net_is_under_test(pin, nets_under_test)
                                    netlist.append(net(pin, isundertest, netid))
                                    netlist[-1].connections.append([device_name, TRANSISTOR_PORTS[i]])
                                    netid = netid + 1
                        elif line.strip().startswith("r") or line.strip().startswith("c") or line.strip().startswith("l"):
                            list_from_line = line.strip().split()
                            device_name = list_from_line[0]
                            for i, pin in enumerate(list_from_line[1:3]):
                                get_netid = pin_is_in_the_list(pin, netlist)
                                if get_netid is not None:
                                    netlist[get_netid].connections.append([device_name, PASSIVE_PORTS[i]])
                                else:
                                    isundertest = net_is_under_test(pin, nets_under_test)
                                    netlist.append(net(pin, isundertest, netid))
                                    netlist[-1].connections.append([device_name, PASSIVE_PORTS[i]])
                                    netid = netid + 1
                        elif line.strip().startswith("x"):
                            pass
                        elif line.strip().startswith(".ends") or line.strip().startswith(".END"):
                            netlist.sort(key=lambda x: x.name)
                            subcircuit_list.append(subcircuit(subcircuit_name, portlist, netlist, subcircuit_id))
                            subcircuit_id = subcircuit_id + 1
                            logging.info("{}" .format(subcircuit_list[-1]))
                        else:
                            pass
    return subcircuit_list


def pin_is_in_the_list(pin, netlist):
    for item in netlist:
        if item.name == pin:
            return item.id
    return None

def net_is_under_test(net, nets_under_test):
    if net in nets_under_test:
        return True
    else:
        return False


def extract_verilog_netlist(design):
    verilogfile = design + ".v"
    tc_directory = "/testcase_" + design + "/"
    module_list = list()
    module_id = 0
    logging.info("Extracting verilog file: {}" .format(verilogfile))

    if not os.path.exists(WORK_DIR + tc_directory + verilogfile):
        logging.critical("{} not found. Quitting ChargeFlow scheme." .format(verilogfile))
        exit()

    with open(WORK_DIR + tc_directory + "nets_under_test.txt", "r") as fnode:
        for line in fnode:
            nets_under_test = line.strip().split()

    with open(WORK_DIR + tc_directory + verilogfile, "r") as fverilog:
        for line in fverilog:
            line = line.strip()
            if line.startswith("//"):
                continue
            elif line.startswith("module"):
                if not line.endswith("global_power;"):
                    module_name = line.split()[1]
                    netlist = list()
                    netid = 0
                    for line in fverilog:
                        if not line == "\n":
                            if line.startswith("endmodule"):
                                netlist.sort(key=lambda x: x.name)
                                module_list.append(module(module_name, portlist, netlist, module_id))
                                module_id = module_id + 1
                                logging.info("{}" .format(module_list[-1]))
                                break
                            elif line.startswith("input"):
                                line = line.replace(",","").replace(";","")
                                portlist = line.split()[1:]
                                # netset = netset.union(portlist)
                            else:
                                list_from_line = line.strip().split()
                                device_name = list_from_line[1]
                                # ismodule = check_if_module(device_name, modulelist)
                                temp_pinlist, temp_netlist = get_net_from_primitive(line)
                                for i, pin in enumerate(temp_netlist): # ignoring body terminal for now
                                    if not temp_pinlist[i] == "B":
                                        get_netid = pin_is_in_the_list(pin, netlist)
                                        if get_netid is not None:
                                            netlist[get_netid].connections.append([device_name, temp_pinlist[i]])
                                        else:
                                            isundertest = net_is_under_test(pin, nets_under_test)
                                            netlist.append(net(pin, isundertest, netid))
                                            netlist[-1].connections.append([device_name, temp_pinlist[i]])
                                            netid = netid + 1
    return module_list

def get_net_from_primitive(line):
    line_splited = line.split()
    nets_in_primitive = list()
    pins_in_primitive = list()
    # logging.info("Extracting module:{}" .format(block_name))
    # print(line)
    for i in range(3, len(line_splited) - 1, 1):
        # print(line_splited[i])
        pin_name, net_name = line_splited[i].split('(')
        nets_in_primitive.append(net_name.strip('),.'))
        pins_in_primitive.append(pin_name.strip('),.'))
    return pins_in_primitive, nets_in_primitive


def prepare_mdlfile(design, subcircuit_list):
    mdlfile = design + ".mdl"
    tc_directory = "/testcase_" + design + "/"
    for item in subcircuit_list:
        if item.name == design:
            export_details = ""
            export_id = 0
            for net in item.netlist:
                if net.isundertest:
                    for connection in net.connections:
                        export_details = export_details + "export real I_" + net.name + "_" + connection[0] + "_" + connection[1] \
                                       + " = I(I1." + connection[0] + ":" + connection[1] + ")\n"
                        export_id = export_id + 1

            with open(WORK_DIR + tc_directory + mdlfile, 'w') as fmdl:
                starting_segment = "\n\nalias measurement get_dc {\n\trun dcOp\n\n"
                ending_segment = "\n}\n\nrun get_dc"
                fmdl.write(starting_segment + export_details + ending_segment)
    return export_id

def get_pin_current_for_nets(design, subcircuit_list):
    logging.info("Extracting currents of each pin of each net...")
    measurefile = design + ".measure"
    tc_directory = "/testcase_" + design + "/"
    variablelist = list()
    currentlist = list()

    with open(WORK_DIR + tc_directory + measurefile, 'r') as fmeasure:
        for line in fmeasure:
            if not line.strip().split() == []:
                temp_var, temp_current = line.strip().split()
                variablelist.append(temp_var.strip())
                currentlist.append(temp_current.strip())
    logging.info("variablelist: {}" .format(variablelist))
    logging.info("currentlist: {}" .format(currentlist))
    for item in subcircuit_list:
        if item.name == design:
            export_details = ""
            export_id = 0
            for net in item.netlist:
                if net.isundertest:
                    logging.info("Net name: {}" .format(net.name))
                    for i, connection in enumerate(net.connections):
                        vut = "I_" + net.name + "_" + connection[0] + "_" + connection[1]
                        # logging.info("vut: {}" .format(vut))
                        if vut in variablelist:
                            index = variablelist.index(vut)
                            net.connections[i].append(currentlist[index])
                            # logging.info("{} {}" .format(variablelist[index], currentlist[index]))
    return subcircuit_list

def run_simulation(design, export_count):
    # export_count = 7
    tc_directory = "/testcase_" + design + "/"
    os.chdir(WORK_DIR + tc_directory)
    # os.system("cp ../outputs/" + design + ".mdl ./")
    os.system("spectremdl -design " + design + "_tb.sp" + " -batch " + design + ".mdl > " + design + ".log")
    os.system("sed -i -n 11," + str(11+export_count) + "p " + design + ".measure")
    os.system("sed -i 's/=//' " + design + ".measure")
    os.chdir(WORK_DIR)
    # os.system("rm -f ./outputs/" + design + ".measure")
    # os.system("cp ./test_example/" + design + ".measure ./outputs/")

def get_pin_to_pin_current(design, subcircuit_list):
    logging.info("Calculating pin to pin current...\n")
    for subcircuit in subcircuit_list:
        if subcircuit.name == design:
            for net in subcircuit.netlist:
                if net.isundertest:
                    logging.info("{}:\n" .format(net.name))
                    source_list = list()
                    sink_list = list()
                    current_from_sources = 0
                    current_from_sinks = 0
                    for connection in net.connections:
                        if float(connection[2]) > 0:
                            source_list.append(connection)
                        elif float(connection[2]) < 0:
                            sink_list.append(connection)
                        else:
                            pass
                    logging.info("Sources: {}\n" .format(source_list))
                    logging.info("Sinks: {}\n" .format(sink_list))

                    for source in source_list:
                        current_from_sources = current_from_sources + abs(float(source[2]))
                    for sink in sink_list:
                        current_from_sinks = current_from_sinks + abs(float(sink[2]))

                    for source in source_list:
                        temp_branch = [source[0:2]]
                        for sink in sink_list:
                            temp_branch.append(sink[0:2])
                            temp_branch_current = abs(float(sink[2])) * abs(float(source[2])) / current_from_sources
                            temp_branch.append(temp_branch_current)
                            net.branchcurrents.append(temp_branch)
    return subcircuit_list


def get_pin_to_pin_current_for_verilog(design, modulelist, subcircuit_list):
    for i, module in enumerate(modulelist):
        if module.name == design:
            module_id = i
            break
    print(modulelist[module_id].branch_under_test)
    for item in modulelist[module_id].branch_under_test:
        netname = item[0]
        d1 = item[1].split('/')[0]
        d2 = item[2].split('/')[0]
        d1_list = d1.split('_')
        d2_list = d2.split('_')
        weight = 0
        for i, net in enumerate(subcircuit_list[-1].netlist):
            if net.name == item[0]:
                netid = i
                break
        for branch in subcircuit_list[-1].netlist[netid].branchcurrents:
            # print(branch[0][0])
            # print(branch[1][0])
            # print(d1_list)
            # print(d2_list)
            if branch[0][0] in d1_list and branch[1][0] in d2_list:
                weight = weight + branch[2]
            elif branch[0][0] in d2_list and branch[1][0] in d1_list:
                weight = weight - branch[2]
            # print(weight)
        item.append(abs(weight))
    print(modulelist[module_id].branch_under_test)

def prepare_print_statement(design, subcircuit_list):
    printfile = design + "_print.inc"
    tc_directory = "/testcase_" + design + "/"
    logging.info("Preparing print file: {}" .format(printfile))

    print_statement = ".PRINT TRAN "
    for subcircuit in subcircuit_list:
        if subcircuit.name == design:
            for net in subcircuit.netlist:
                if net.isundertest:
                    for connection in net.connections:
                        print_statement = print_statement + "I" + connection[1] + "(I1." + connection[0] + ") "
    logging.info("{}" .format(print_statement))

    with open(WORK_DIR + tc_directory + printfile, 'w') as fprint:
        fprint.write(print_statement)

def generate_tran_data(design):
    # export_count = 7
    tc_directory = "/testcase_" + design + "/"
    tbfile_old = design + "_tb.sp"
    tbfile_new = design + "_revised_tb.sp"
    os.chdir(WORK_DIR + tc_directory)

    tb_details = ""
    with open(WORK_DIR + tc_directory + tbfile_old, 'r') as ftb_old:
        for line in ftb_old:
            tb_details = tb_details + line
    tb_details = tb_details + "\n" + "include \"./" + design + "_print.inc\"\n"

    logging.info("Doing transient simulations..." )
    with open(WORK_DIR + tc_directory + tbfile_new, 'w') as ftb_new:
        ftb_new.write(tb_details)
    os.system("spectre " + tbfile_new + " > " + design + ".log")
    # os.system("sed -i -n 11," + str(11+export_count) + "p " + design + ".measure")
    # os.system("sed -i 's/=//' " + design + ".measure")
    # os.chdir(WORK_DIR)

def get_branch_current_from_verilog(design, modulelist, net_from_spice, branchcurrents_from_spice):
    cfconst_for_each_net = list()
    for module in modulelist:
        if module.name == design:
            for net in module.netlist:
                if net.isundertest and net.name == net_from_spice:
                    device_list = list()
                    for connection in net.connections:
                            device_list.append(connection[0].split('_'))
                    # print(device_list)
                    for branchcurrent in branchcurrents_from_spice:
                        # print(branchcurrent)
                        block_id1 = -99
                        block_id2 = -98
                        for i, item in enumerate(device_list):
                            # print(item)
                            if branchcurrent[0] in item:
                                block_id1 = i
                            if branchcurrent[2] in item:
                                block_id2 = i
                        if block_id1 > -1 and block_id2 > -1:
                            if not block_id1 == block_id2:
                                str1 = net.connections[block_id1][0] + "/" + net.connections[block_id1][1]
                                str2 = net.connections[block_id2][0] + "/" + net.connections[block_id2][1]
                                cfconst_for_each_net.append(net.name + " " + str1 + " " + str2 + " " + str(abs(branchcurrent[4])))
                                flag = 0
                                for item in net.branchcurrents:
                                    if item[0] == str1 and item[1] == str2:
                                        item[2] = item[2] + abs(branchcurrent[4])
                                        flag = 1
                                        break
                                if flag == 0:
                                    net.branchcurrents.append([str1, str2, abs(branchcurrent[4])])

                                ### Changes from here


    return cfconst_for_each_net

def prepare_cfconst(design, modulelist):
    tc_directory = "/testcase_" + design + "/"
    cfconstfile = design + ".cfconst"
    cfconst = ""
    for module in modulelist:
        if module.name == design:
            for net in module.netlist:
                if net.isundertest:
                    for branch in net.branchcurrents:
                        cfconst = cfconst + net.name + "\t" + branch[0] + "\t" + branch[1] + "\t" + str(branch[2]) + "\n"


    with open(WORK_DIR + tc_directory + cfconstfile, 'w') as fcfconst:
        # print(cfconst)
        fcfconst.write(cfconst)
    return cfconst

def store_pin_currents_in_csv(design, subcircuit_list):
    """
    This function just extracts pin current from the transient file generated
    by the spice transient simulation, does necessary string replacements,
     and saves the data in csv format.
    """
    logging.info("Generating branch currents from spice...")
    tc_directory = "/testcase_" + design + "/"
    printfile = design + "_revised_tb.print"
    os.chdir(WORK_DIR + tc_directory)
    if os.path.exists(WORK_DIR + tc_directory + "pin_currents.txt"):
        os.system("rm -f pin_currents.txt")
    os.system("grep -vwE \"(\*|x|y)\" " + printfile + " > pin_currents.txt" )
    num_lines = sum(1 for line in open('pin_currents.txt'))

    # with open("pin_currents.txt", 'r') as fpin:
    blocks_in_transients = open("pin_currents.txt", 'r').read().count("time")
    # blocks_in_transients = temp.count("time")
    points_in_transients = int(num_lines/int(blocks_in_transients))
    logging.info("Blocks in PRINT file: {}" .format(blocks_in_transients))
    logging.info("Points in PRINT file: {}" .format(points_in_transients))

    """Create a dataframe consisting pin currents"""
    with open(WORK_DIR + tc_directory + "pin_currents.txt", 'r') as fpinc:
        lines = fpinc.readlines()
        rearranged_lines = ""
        for i in range(points_in_transients):
            # line = ""
            for j in range(blocks_in_transients):
                line_to_read = j*points_in_transients + i
                lines_string = lines[line_to_read].strip().replace(' m', 'e-3')
                lines_string = lines_string.replace(' u', 'e-6').replace(' n', 'e-9').replace(' p', 'e-12').replace(' f', 'e-15').replace(' a', 'e-18')
                templine = re.split(" +", lines_string.strip())
                if j == 0:
                    # rearranged_lines = rearranged_lines + ":".join(re.split("  +", lines[line_to_read].strip()))
                    rearranged_lines = rearranged_lines + ":".join(templine)
                else:
                    # print(lines[line_to_read].strip().split('\t'))
                    # rearranged_lines = rearranged_lines + ":" + ":".join(re.split("  +", lines[line_to_read].strip())[1:])
                    rearranged_lines = rearranged_lines + ":" + ":".join(templine[1:])
            rearranged_lines = rearranged_lines + "\n"
        # print(rearranged_lines)
    with open(WORK_DIR + tc_directory + "pin_currents_new.csv", 'w') as fpinc:
        lines = fpinc.writelines(rearranged_lines)

def generate_branch_current_at_each_time_stamp(design, subcircuit_list):
    """
    This function estimates branch current from pin to pin for each time
    stamp of transient simulation. In the process, it considers each point in
    time stamp as isolated; identifies source/sinks for that point; measures
    branch current from source to sink for that point.

    """
    tc_directory = "/testcase_" + design + "/"
    all_branch_currents_df = pd.read_csv(WORK_DIR + tc_directory + "pin_currents_new.csv", delimiter= ':', usecols=['time'])
    for subcircuit in subcircuit_list:
        if subcircuit.name == design:
            for net in subcircuit.netlist:
                if net.isundertest:
                    clmns_under_test = list()
                    for connection in net.connections:
                        clmns_under_test.append("i" + connection[1] \
                                                + "(I1." + connection[0] + ")")
                    logging.info("For net {}, columns under test: {}\n"
                                 .format(net.name, clmns_under_test))
                    # print("For net {}, columns under test: {}\n"
                    #              .format(net.name, clmns_under_test))
                    temp_branches_under_test = itertools.combinations(clmns_under_test, 2)
                    branch_current_under_test = list()
                    for item in temp_branches_under_test:
                        branch_current_under_test.append("_".join(item))
                    branch_current_under_test_dict = dict.fromkeys(branch_current_under_test, 0)
                    branch_current_under_test_df = pd.DataFrame(columns = branch_current_under_test)
                    # print(branch_current_under_test_dict)
                    # print(branch_current_under_test_df)
                    logging.info("Branches:\n{}\n" .format(branch_current_under_test))

                    with open(WORK_DIR + tc_directory + "pin_currents_new.csv") as fpincurrents:
                        reader = csv.DictReader(fpincurrents, delimiter = ':')
                        for row in reader:
                            # print(row)
                            source_list = list()
                            sink_list = list()
                            total_current = 0
                            for item in clmns_under_test:
                                # print("item: {}, value: {}" .format(item, row[item]))
                                if float(row[item]) > 0: # In transient data of spice, if a current goes in of  a pin, it is shown with positive value. However, the pin is acting as a sink.
                                    sink_list.append(item)
                                elif float(row[item]) <= 0: # In transient data of spice, if a current goes out of  a pin, it is shown with negative value. However, the pin is acting as a source.
                                    source_list.append(item)
                                    total_current = total_current + -1*float(row[item])
                                else:
                                    pass
                            # print("{}:" .format(net.name))
                            # print("Sources: {}, Sinks: {}, Current: {}"
                            #       .format(source_list, sink_list, total_current))
                            # breakpoint()

                            for source in source_list:
                                for sink in sink_list:
                                    temp_branch_current = float(row[sink])*float(row[source])/total_current
                                    if source + "_" + sink in branch_current_under_test:
                                        branch_current_under_test_dict[source + "_" + sink] = temp_branch_current
                                    elif sink + "_" + source in branch_current_under_test:
                                        branch_current_under_test_dict[sink + "_" + source] = -1*temp_branch_current
                                    else:
                                        pass
                            # print(branch_current_under_test_dict)
                            branch_current_under_test_df = branch_current_under_test_df.append(
                                                        branch_current_under_test_dict,
                                                        ignore_index = True)
                    for item in branch_current_under_test_df.columns:
                        # temp_array = branch_current_under_test_df[item].to_numpy()
                        temp_rms = np.sqrt(np.mean(np.square(branch_current_under_test_df[item].to_numpy())))
                        logging.info("Branch: {}, RMS current: {}" .format(item, temp_rms))
                        source_details = item.split('_')[0].lstrip('i').rstrip(')').replace("I1", "").replace("(", "").split(".")
                        sink_details = item.split('_')[1].lstrip('i').rstrip(')').replace("I1", "").replace("(", "").split(".")
                        source_details.reverse()
                        sink_details.reverse()
                        logging.info("Branch: {} >> {} " .format(source_details, sink_details))
                        temp_list = source_details + sink_details
                        # temp_list.append(temp_rms)
                        net.branchcurrents.append(temp_list)
                    # print(branch_current_under_test_df)
                    all_branch_currents_df = pd.concat([all_branch_currents_df,\
                                                        branch_current_under_test_df],
                                                        axis = 1 )
            # print(all_branch_currents_df)
            all_branch_currents_df.to_csv(WORK_DIR + tc_directory
                                          + "branch_currents.csv",
                                           index = False, mode = 'w')

    # df_test = pd.read_csv(WORK_DIR + tc_directory + "pin_currents_new.csv", delimiter= ':', usecols=['time'])
    # print("Delta t:\n")
    # print(df_test[0:].head())
    # print(df_test[1:-1].head())
    # temp_np_array = df_test[0:-1].values - df_test[1:].values
    # print(temp_np_array)

    return subcircuit_list

def get_branch_current_for_verilog_at_each_time_stamp(WORK_DIR, design, modulelist, net_from_spice, branchcurrents_from_spice):
    logging.info("Calculating branch currents for verilog...")
    tc_directory = "/testcase_" + design + "/"
    all_branch_currents_spice_df = pd.read_csv(WORK_DIR + tc_directory + "branch_currents.csv")
    all_branch_currents_verilog_df = pd.DataFrame()
    cfconst_for_each_net = list()
    for module in modulelist:
        if module.name == design:
            for net in module.netlist:
                if net.isundertest and net.name == net_from_spice:
                    device_list = list()
                    for connection in net.connections:
                            device_list.append(connection[0].split('_'))
                    # # print(device_list)
                    for branchcurrent in branchcurrents_from_spice:
                        # print(branchcurrent)
                        block_id1 = -99
                        block_id2 = -98
                        for i, item in enumerate(device_list):
                            # print(item)
                            if branchcurrent[0] in item:
                                block_id1 = i
                            if branchcurrent[2] in item:
                                block_id2 = i
                        if block_id1 > -1 and block_id2 > -1:
                            if not block_id1 == block_id2:
                                str1 = net.connections[block_id1][0] + "/" + net.connections[block_id1][1]
                                str2 = net.connections[block_id2][0] + "/" + net.connections[block_id2][1]
                                str3 = net.name + "-" + str1 + "-" + str2
                                str4 = net.name + "-" + str2 + "-" + str1
                                str5 = "i" + branchcurrent[1] + "(I1." + branchcurrent[0] + ")_" + "i" + branchcurrent[3] + "(I1." + branchcurrent[2] + ")"
                                new_df = all_branch_currents_spice_df[[str5]]
                                # print(str5)
                                # print(new_df)
                                # new_df = new_df.rename(columns = {str5: str3})
                                # print("New dataframe:\n{}" .format(new_df))
                                if str3 in all_branch_currents_verilog_df.columns:
                                    new_df = new_df.rename(columns = {str5: str3})
                                    sum = all_branch_currents_verilog_df[str3] + new_df[str3]
                                    all_branch_currents_verilog_df[str3] = sum
                                    # print("Branch current after addition:\n{}" .format(all_branch_currents_verilog_df))
                                    # print(all_branch_currents_verilog_df)
                                    pass
                                elif str4 in all_branch_currents_verilog_df.columns:
                                    new_df = new_df.rename(columns = {str5: str4})
                                    sum = all_branch_currents_verilog_df[str4] + (-1)*new_df[str4]
                                    all_branch_currents_verilog_df[str4] = sum
                                    # print("Branch current after addition:\n{}" .format(all_branch_currents_verilog_df))
                                    # print(all_branch_currents_verilog_df)
                                    pass
                                else:
                                    new_df = new_df.rename(columns = {str5: str3})
                                    all_branch_currents_verilog_df = pd.concat([all_branch_currents_verilog_df, new_df], axis = 1)
                                    # print("Branch current after append:\n{}" .format(all_branch_currents_verilog_df))
                    if not all_branch_currents_verilog_df.empty:
                        if not os.path.exists(WORK_DIR + tc_directory + "branch_currents_verilog.csv"):
                            temp_df = all_branch_currents_spice_df["time"]
                            temp_df = pd.concat([temp_df, all_branch_currents_verilog_df], axis = 1)
                            temp_df.to_csv(WORK_DIR + tc_directory
                                                  + "branch_currents_verilog.csv",
                                                   index = False, mode = 'w')
                            # breakpoint()
                        else:
                            temp_df = pd.read_csv(WORK_DIR + tc_directory + "branch_currents_verilog.csv")
                            temp_df = pd.concat([temp_df, all_branch_currents_verilog_df], axis = 1)
                            # print(temp_df.head())
                            temp_df.to_csv(WORK_DIR + tc_directory
                                                  + "branch_currents_verilog.csv",
                                                   index = False, mode = 'w')
                    for item in all_branch_currents_verilog_df.columns:
                        netname, prim1, prim2 = item.split('-')
                        squared_current = np.square(all_branch_currents_verilog_df[item].to_numpy())
                        time = all_branch_currents_spice_df["time"].to_numpy()
                        delta_time = time[1:] - time[0:-1]
                        area_of_the_transient = np.sum(0.5*(np.multiply(squared_current[1:] + squared_current[0:-1], delta_time)))
                        rms_current_from_int = np.sqrt(area_of_the_transient/(time[-1] - time[0]))
                        rms_current = np.sqrt(np.mean(np.square(all_branch_currents_verilog_df[item].to_numpy())))
                        templist = [prim1, prim2, rms_current_from_int]
                        # print("RMS current regular: {}, RMS current from area: {}" .format(rms_current, rms_current_from_int))
                        # print("{} {} {}" .format(templist, netname, rms_current))
                        net.branchcurrents.append(templist)
    # return modulelist

def purge(design):
    logging.info("Purging...")
    tc_directory = "/testcase_" + design + "/"
    for f in os.listdir(WORK_DIR + tc_directory):
        if re.search("pin_currents*", f) or \
           re.search("branch_currents*", f) or \
           re.search(design + "_tb.print", f) or \
           re.search(design + "_revised_tb.print", f):
            os.remove(os.path.join(WORK_DIR + tc_directory, f))

def display_constraints_after_sort(design):
    # logging.info("Calculating branch currents for verilog...")
    tc_directory = "/testcase_" + design + "/"
    all_constraints = pd.read_csv(WORK_DIR + tc_directory + design + ".cfconst", header = None, delimiter = '\s+')
    all_constraints.columns = ["Net", "Pin1", "Pin2", "RMS"]
    all_constraints = all_constraints.sort_values(by=['RMS'], ascending = False)
    print(all_constraints)


def main():
    logging.info('Starting ChargeFlow...')
    purge(args.design)
    subcircuit_list = extract_spice_netlist(args.design)
    modulelist = extract_verilog_netlist(args.design)
    prepare_print_statement(args.design, subcircuit_list)
    generate_tran_data(args.design)
    store_pin_currents_in_csv(args.design, subcircuit_list)
    subcircuit_list = generate_branch_current_at_each_time_stamp(args.design, subcircuit_list)
    for subcircuit in subcircuit_list:
        if subcircuit.name == args.design:
            for net in subcircuit.netlist:
                if net.isundertest:
                    # get_branch_current_from_verilog(args.design, modulelist, net.name, net.branchcurrents)
                    get_branch_current_for_verilog_at_each_time_stamp(WORK_DIR, args.design, modulelist, net.name, net.branchcurrents)
    # # print(cfconst)
    cfconst = prepare_cfconst(args.design, modulelist)
    logging.info("ChargeFlow Constraints:\n{}" .format(cfconst))
    display_constraints_after_sort(args.design)
    # print("From spice:")
    # for subcircuit in subcircuit_list:
    #     if subcircuit.name == args.design:
    #         for net in subcircuit.netlist:
    #             if net.isundertest:
    #                 print(net)
    #
    # print("From verilog:")
    # for module in modulelist:
    #     if module.name == args.design:
    #         for net in module.netlist:
    #             if net.isundertest:
    #                 print(net)


if __name__ == "__main__":
    main()
