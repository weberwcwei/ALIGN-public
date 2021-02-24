import logging
import argparse
import timeit
import os
import pandas as pd
import itertools
import math
import re

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
TRANSISTOR_PORTS = {0: "1", 1: "3"} # ignoring gate and body connections for now
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

def prepare_cfconst(design, modulelist):
    temp_dict = dict()
    tc_directory = "/testcase_" + design + "/"
    with open(WORK_DIR + tc_directory + "nets_under_test.txt","r") as fnode:
        for line in fnode:
            nets_under_test = line.strip().split()

    for module in modulelist:
        if module.name == args.design:
            if not os.path.exists(WORK_DIR + "/outputs"):
                os.mkdir(WORK_DIR + "/outputs")
            else:
                os.chdir(WORK_DIR + tc_directory)
                with open(design + ".cfconst", 'w') as fcfconst:
                    for net in module.netset:
                        if net in nets_under_test:
                            temp_list = list()
                            for primitive in module.primitivelist:
                                if net in primitive.connections:
                                    if not primitive.connections[net] == "B":
                                        temp_list.append(primitive.block_name + "/" + primitive.connections[net])
                            temp_dict[net] = temp_list
                    # print(temp_dict)
                    for item in temp_dict:
                        line = ""
                        pin_combos = list(itertools.combinations(temp_dict[item], 2))
                        # print(pin_combos)
                        for pin_combo in list(pin_combos):
                            fcfconst.write(item + "    " + pin_combo[0] + "    " + pin_combo[1] + "\n")
                            module.branch_under_test.append([item, pin_combo[0], pin_combo[1]])
    return modulelist


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
                            temp_list_with_drain_source = [list_from_line[1], list_from_line[3]]
                            device_name = list_from_line[0]
                            for i, pin in enumerate(temp_list_with_drain_source): # ignoring body terminal for now
                                get_netid = pin_is_in_the_list(pin, netlist)
                                if get_netid is not None:
                                    netlist[get_netid].connections.append([device_name, TRANSISTOR_PORTS[i]])
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
                                    get_netid = pin_is_in_the_list(pin, netlist)
                                    if get_netid is not None:
                                        netlist[get_netid].connections.append([device_name, temp_pinlist[i]])
                                    else:
                                        isundertest = net_is_under_test(pin, nets_under_test)
                                        netlist.append(net(pin, isundertest, netid))
                                        netlist[-1].connections.append([device_name, temp_pinlist[i]])
                                        netid = netid + 1
    return module_list
# def extract_verilog_netlist(design):
#     verilog_file = args.design + ".v"
#     tc_directory = "/testcase_" + design + "/"
#     logging.info("Extracting verilog file: {}" .format(verilog_file))
#     module_list = list()
#
#     if not os.path.exists(WORK_DIR + tc_directory + verilog_file):
#         logging.critical("{} not found. Quitting ChargeFlow scheme." .format(verilog_file))
#         exit()
#
#     with open(WORK_DIR + tc_directory + verilog_file) as fverilog:
#         for line in fverilog:
#             line = line.strip()
#             if line.startswith("//"):
#                 continue
#             elif line.startswith("module"):
#                 if not line.endswith("global_power;"):
#                     module_name = line.split()[1]
#                     primitivelist = list()
#                     netset = set()
#                     for line in fverilog:
#                         if not line == "\n":
#                             if line.startswith("endmodule"):
#                                 modulelist.append(module(module_name, portlist, primitivelist, netset))
#                                 break
#                             elif line.startswith("input"):
#                                 line = line.replace(",","").replace(";","")
#                                 portlist = line.split()[1:]
#                                 netset = netset.union(portlist)
#                             else:
#                                 ismodule = check_if_module(line, modulelist)
#                                 netset = netset.union(get_net_from_primitive(line))
#                                 primitivelist.append(extract_primitive(module_name, line, ismodule))
#     return modulelist

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
            # breakpoint()
            if branch[0][0] in d1_list and branch[1][0] in d2_list:
                weight = weight + branch[2]
            elif branch[0][0] in d2_list and branch[1][0] in d1_list:
                weight = weight - branch[2]
            # print(weight)
            # breakpoint()
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

def extract_print_file(design, subcircuit_list):
    tc_directory = "/testcase_" + design + "/"
    printfile = design + "_revised_tb.print"
    os.chdir(WORK_DIR + tc_directory)
    if os.path.exists(WORK_DIR + tc_directory + "pin_currents.txt"):
        os.system("rm -f pin_currents.txt")
    os.system("grep -vwE \"(\*|x|y)\" " + printfile + " > pin_currents.txt" )
    num_lines = sum(1 for line in open('pin_currents.txt'))

    total_pin_under_test = 0
    for subcircuit in subcircuit_list:
        if subcircuit.name == design:
            for net in subcircuit.netlist:
                if net.isundertest:
                    total_pin_under_test = total_pin_under_test + len(net.connections)
    blocks_in_transients = math.ceil((total_pin_under_test+1)/5)
    points_in_transients = int(num_lines/blocks_in_transients)

    """Create a dataframe consisting pin currents"""
    with open(WORK_DIR + tc_directory + "pin_currents.txt", 'r') as fpinc:
        lines = fpinc.readlines()
        rearranged_lines = ""
        for i in range(points_in_transients):
            # line = ""
            for j in range(blocks_in_transients):
                line_to_read = j*points_in_transients + i
                templine = re.split("  +", lines[line_to_read].strip())
                templine = [sub.replace(' u', 'e-6') for sub in templine]
                templine = [sub.replace(' n', 'e-9') for sub in templine]
                templine = [sub.replace(' p', 'e-12') for sub in templine]
                templine = [sub.replace(' f', 'e-15') for sub in templine]
                if j == 0:
                    # rearranged_lines = rearranged_lines + ":".join(re.split("  +", lines[line_to_read].strip()))
                    rearranged_lines = rearranged_lines + ":".join(templine)
                else:
                    # print(lines[line_to_read].strip().split('\t'))
                    # rearranged_lines = rearranged_lines + ":" + ":".join(re.split("  +", lines[line_to_read].strip())[1:])
                    rearranged_lines = rearranged_lines + ":" + ":".join(templine[1:])
            rearranged_lines = rearranged_lines + "\n"
        print(rearranged_lines)
    with open(WORK_DIR + tc_directory + "pin_currents_new.csv", 'w') as fpinc:
        lines = fpinc.writelines(rearranged_lines)
    # with open(WORK_DIR + tc_directory + "pin_currents_new.csv", 'r') as fpinc:
    df = pd.read_csv(WORK_DIR + tc_directory + "pin_currents_new.csv", delimiter=":")
    df = df.astype(float).multiply(-1)
    # print(df.columns)

    """Create branch currents from pin currents"""
    for subcircuit in subcircuit_list:
        if subcircuit.name == design:
            for net in subcircuit.netlist:
                if net.isundertest:
                    clmns_under_test = list()
                    source_list = list()
                    sink_list = list()
                    for connection in net.connections:
                        clmns_under_test.append("i" + connection[1] + "(I1." + connection[0] + ")")
                    df_under_test = df[clmns_under_test]
                    for item in clmns_under_test:
                        if df_under_test.loc[1:,item].values[0] < 0:
                            sink_list.append(item)
                        elif df_under_test.loc[1:,item].values[0] > 0:
                            source_list.append(item)
                        else:
                            pass

                    df_sum_sources = df[source_list].sum(axis = 1)
                    df_sum_sources_numpy = df_sum_sources.to_numpy()
                    df_branch = pd.DataFrame()
                    # print(df_sum_sources_numpy)
                    for source in source_list:
                        df_source_numpy = df[source].to_numpy()
                        for sink in sink_list:
                            df_sink_numpy = df[sink].to_numpy()
                            df_temp_numpy = df_sink_numpy * df_source_numpy / df_sum_sources_numpy
                            # print(df_temp_numpy.shape)
                            branch_name = str(source + "_" + sink).split()
                            # print()
                            df_temp = pd.DataFrame(df_temp_numpy, columns = branch_name)
                            # print(df_temp.head())
                            df_branch = pd.concat([df_branch, df_temp], axis=1)
                    print(df_branch.head())



def main():
    logging.info('Starting ChargeFlow...')
    subcircuit_list = extract_spice_netlist(args.design)
    modulelist = extract_verilog_netlist(args.design)
    prepare_print_statement(args.design, subcircuit_list)
    generate_tran_data(args.design)
    extract_print_file(args.design, subcircuit_list)
    # modulelist = prepare_cfconst(args.design, modulelist)
    # for item in modulelist:
    #     logging.info("Module Details:\n{}" .format(item))
    # subcircuit_list = extract_spice_netlist(args.design)
    # # export_count = prepare_mdlfile(args.design, subcircuit_list)
    # export_count = 8
    # run_simulation(args.design, export_count)
    # subcircuit_list = get_pin_current_for_nets(args.design, subcircuit_list)
    # subcircuit_list = get_pin_to_pin_current(args.design, subcircuit_list)
    # get_pin_to_pin_current_for_verilog(args.design, modulelist, subcircuit_list)
    # for item in subcircuit_list:
    #     print(item)


if __name__ == "__main__":
    main()
