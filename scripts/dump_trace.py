#!/usr/bin/env python
# -*-coding:utf-8 -*-

import os
import sys
import re
from collections import namedtuple
from collections import defaultdict
from collections import OrderedDict
import datetime
import json
from wban_pram import *

nested_defaultdict = lambda: defaultdict(nested_defaultdict)


def get_fn_info(trace):
    """get the *.trace info

    input: wban_raw_data/wban-N4x2_ver1_hybrid_exp-DES-6-2015_06_02_02_21.trace
    """
    trace_fn = os.path.basename(trace)
    raw = re.split('[.-]', trace_fn)
    scenario = raw[1]
    des = raw[3]
    timestamp = raw[4]
    # network, version, MAC, traffic arrival function
    net, ver, mac, tf = scenario.split('_')
    scene = {'net': net, 'ver': ver, 'mac': mac,
             'tf': tf, 'des': des, 'timestamp': timestamp}
    return scene


def get_basic_info(line):
    """get basic info before submode"""
    raw = re.split('[,=]', line)
    t = float(raw[1])
    node_name = raw[3]
    bid = raw[5]
    nid = raw[7]
    node_id = raw[9]
    mode = raw[10]
    submode = raw[11]
    basic_info = {'t': t, 'node_name': node_name,
                  'bid': bid, 'nid': nid, 'nodeid': node_id,
                  'mode': mode, 'submode': submode}
    return [raw, basic_info]


def get_src(line):
    """get the source traffic parameters"""
    Stat = namedtuple('Stat', 'interval size start_t stop_t')
    raw, basic_info = get_basic_info(line)
    tf_stop_t = float(raw[-1])
    tf_start_t = float(raw[-3])
    tf_size_raw = filter(None, re.split('[(  )]', raw[-5]))
    tf_size = {'f': tf_size_raw[0], 'mean': float(tf_size_raw[1])}
    tf_interval_raw = filter(None, re.split('[(  )]', raw[-7]))
    tf_interval = {'f': tf_size_raw[0], 'mean': float(tf_interval_raw[1])}
    stat = Stat._make((tf_interval, tf_size, tf_start_t, tf_stop_t))
    up = raw[-9]
    src = basic_info
    src['src'] = {'up': up, 'stat': stat}
    return src


def get_sv_data(line):
    """get sv data statistics"""
    Stat = namedtuple('Stat', 'num ppdu_kb')
    raw, basic_info = get_basic_info(line)
    ppdu_kb = float(raw[-1])
    num = float(raw[-3])
    stat = Stat._make((num, ppdu_kb))
    state = raw[-5]
    up = raw[-7]
    sv_data = basic_info
    sv_data['sv_data'] = {'up': up, 'state': state, 'stat': stat}
    return sv_data


def get_hb_data(line):
    """get hb data statistics"""
    Stat = namedtuple('Stat', 'num ppdu_kb')
    raw, basic_info = get_basic_info(line)
    ppdu_kb = float(raw[-1])
    num = float(raw[-3])
    stat = Stat._make((num, ppdu_kb))
    state = raw[-5]
    up = raw[-7]
    hb_data = basic_info
    hb_data['hb_data'] = {'up': up, 'state': state, 'stat': stat}
    return hb_data


def get_lat(line):
    """get latency of data packets"""
    raw, basic_info = get_basic_info(line)
    lat_avg = float(raw[-1])
    up = raw[-3]
    lat = basic_info
    lat['lat'] = {'up': up, 'stat': lat_avg}
    return lat


def get_energy(line):
    """get energy of whole process"""
    Stat = namedtuple('Stat', 'tx rx cca idle sleep remainning total')
    raw, basic_info = get_basic_info(line)
    total = float(raw[-1])
    remainning = float(raw[-3])
    sleep = float(raw[-5])
    idle = float(raw[-7])
    cca = float(raw[-9])
    rx = float(raw[-11])
    tx = float(raw[-13])
    stat = Stat._make((tx, rx, cca, idle, sleep, remainning, total))
    energy = basic_info
    energy['energy'] = {'stat': stat}
    return energy


def get_throughput(line):
    """get throughput of all up data packet"""
    Stat = namedtuple('Stat', 'msdu ppdu')
    raw, basic_info = get_basic_info(line)
    ppdu_kb = float(raw[-1])
    msdu_kb = float(raw[-3])
    stat = Stat._make((msdu_kb, ppdu_kb))
    throughput = basic_info
    throughput['throughput'] = {'stat': stat}
    return throughput


def is_hub(line):
    """Hub: nid < 32"""
    raw, basic_info = get_basic_info(line)
    nid = basic_info['nid']
    if nid < 32:
        return True
    else:
        return False


def get_stat(trace):
    """get statistics of trace files"""
    trace_info = nested_defaultdict()
    trace_info['scene'] = get_fn_info(trace)
    with open(trace, 'r') as f:
        for line in f:
            basic_info = get_basic_info(line)[1]
            bid = basic_info['bid']
            nid = basic_info['nid']
            trace_info[bid][nid]['t'] = basic_info['t']
            trace_b_n = trace_info[bid][nid]
            if re.search('init,src', line):
                src = get_src(line)
                up = src['src']['up']
                trace_info[bid][nid]['src'][up] = src['src']['stat']
            elif re.search('stat,sv_data', line):
                sv_data = get_sv_data(line)
                up = sv_data['sv_data']['up']
                state = sv_data['sv_data']['state']
                trace_b_n['sv_data'][up][state] = sv_data['sv_data']['stat']
            elif re.search('stat,hb_data', line):
                hb_data = get_hb_data(line)
                up = hb_data['hb_data']['up']
                state = hb_data['hb_data']['state']
                trace_b_n['hb_data'][up][state] = hb_data['hb_data']['stat']
            elif re.search('stat,latency', line):
                lat = get_lat(line)
                up = lat['lat']['up']
                trace_b_n['lat'][up] = lat['lat']['stat']
            elif re.search('stat,throughput', line):
                throughput = get_throughput(line)
                trace_b_n['throughput'] = throughput['throughput']['stat']
            elif re.search('stat,energy', line):
                energy = get_energy(line)
                trace_b_n['energy'] = energy['energy']['stat']
    return trace_info


def get_trace_files(raw_dir):
    """get trace files from raw_data path"""
    if os.path.isfile(raw_dir):
        print "Usage: dump_stat.py raw_data_dir [stat_dump_dir]"
        sys.exit(1)
    trace_files = []
    subdir_files = os.listdir(raw_dir)
    for trace in subdir_files:
        trace_path = os.path.join(raw_dir, trace)
        if os.path.isdir(trace_path):
            print("!!! Skip trace_dir: %s !!!") % trace_path
        elif re.search('.trace$', trace_path):
            trace_files.append(trace_path)
        else:
            print("!!! Skip non-trace file: %s !!!") % trace_path
    return trace_files


def get_trace_infos(raw_dir):
    trace_files = get_trace_files(raw_dir)
    trace_infos = []
    for i, trace in enumerate(trace_files):
        trace_fn = os.path.basename(trace)
        progress = 1.0 * (i + 1) / len(trace_files)
        print("progress %f, processing %s...") % (progress, trace_fn)
        trace_infos.append(get_stat(trace))
    return trace_infos


def make_dir(path_in):
    if not os.path.exists(path_in):
        print("mkdir %s...") % path_in
        os.makedirs(path_in)


def dump_stat(raw_dir, stat_dir=None):
    if not stat_dir:
        stat_dir_par = os.path.abspath(os.path.join(raw_dir, os.pardir))
        stat_dir = os.path.join(stat_dir_par, 'stat_dump')
        make_dir(stat_dir)
    if not os.path.isdir(stat_dir):
        print("!!!stat_dir %s is not a valid dir!!!") % stat_dir
        sys.exit(1)
    today = str(datetime.date.today())
    stat_fn = 'stat_' + today + '.json'
    stat_path = os.path.join(stat_dir, stat_fn)
    print("stat_path: %s") % stat_path
    with open(stat_path, 'wb') as f:
        trace_infos = get_trace_infos(raw_dir)
        json.dump(trace_infos, f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) > 3 or len(sys.argv) == 1:
        print "Usage: %s raw_data_dir [stat_dump_dir]" % (sys.argv[0])
        sys.exit(1)
    else:
        stat_dump_dir = None
        raw_data_dir = sys.argv[1]
        if os.path.isfile(raw_data_dir):
            print "Usage: %s raw_data_dir [stat_dump_dir]" % (sys.argv[0])
            sys.exit(1)
        if len(sys.argv) == 3:
            stat_dump_dir = sys.argv[2]
        dump_stat(raw_data_dir, stat_dump_dir)
