from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
import os
from os.path import join, exists
import platform
import json
import mx

from mx_zippy_bench_param import benchmarks_list


importerror = False
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from functools import reduce
except:
    importerror = True

debug = False

_mx_graal = mx.suite("graal-core", fatalIfMissing=False)
_suite = mx.suite('zippy')

asv_env = os.environ.get("ZIPPY_ASV_PATH")
if not asv_env:
    asv_env = _suite.dir

asv_dir = asv_env + '/asv/'
asv_results_dir = asv_dir + '/results/'

machine_name = os.environ.get("MACHINE_NAME")
if not machine_name:
    machine_name = platform.node()

machine_name += '-no-graal' if not _mx_graal else '-graal'
machine_results_dir = asv_results_dir + machine_name

chart_dir = asv_env + '/graphs/' + machine_name + '/'

commit_hash = _suite.vc.parent(_suite.dir)

if not importerror:
    geomean = lambda s: reduce(lambda x,y: x*y, s) ** (1.0 / len(s))


def plot_scales_sub(_params, _bench_params):
    r_bench_params = []
    for _param in _params:
        r_bench_params += [_bench_params[_param]]
    return r_bench_params


def plot_scales(benchmarks, all_benchmarks_list, color_hatch_marker):
    for _type in benchmarks:
        for _timing in benchmarks[_type]:
            _bench_axs = {}
            for _bench in all_benchmarks_list[_type][_timing]:
                if isinstance(all_benchmarks_list[_type][_timing][_bench], list):
                    _bench_axs[_bench] = None
            if not _bench_axs:
                continue
            subplots_count = len(_bench_axs)
            fig, axs = plt.subplots(subplots_count, 1, figsize=(5, 5 * subplots_count))
            fig.subplots_adjust(left=0.08, right=0.98, wspace=0.3, hspace=0.5)
            axs_i = 0
            for _bench in sorted(_bench_axs.keys()):
                _bench_axs[_bench] = axs[axs_i]
                axs_i += 1

            for _interp in benchmarks[_type][_timing]:
                for _bench in benchmarks[_type][_timing][_interp]:
                    if isinstance(all_benchmarks_list[_type][_timing][_bench], list):
                        ax = _bench_axs[_bench]
                        _params = all_benchmarks_list[_type][_timing][_bench]
                        r_bench_params = plot_scales_sub(_params, benchmarks[_type][_timing][_interp][_bench])
                        marker = color_hatch_marker[_interp][2]
                        color  = color_hatch_marker[_interp][0]
                        ax.plot(_params, r_bench_params, marker, color=color, label=_interp)

            for _bench in sorted(_bench_axs.keys()):
                ax = _bench_axs[_bench]
                ax.legend(loc='upper left')
                ax.set_yscale('linear') # 'log'
                ax.set_title(_bench)
                ax.grid(True)

            fig.savefig(chart_dir + 'benchmarks_scales_' + _type + '_' + _timing + '.png', bbox_inches='tight')
            fig.savefig(chart_dir + 'benchmarks_scales_' + _type + '_' + _timing + '.pdf', format='pdf', bbox_inches='tight')



def plot_bar_speedups(ax, benchmarks, all_benchmarks_list, interpreter_list, color_hatch, witdh, small=False):
    ax.xaxis.tick_top()
    ax.tick_params(labeltop='off')
    ax.xaxis.tick_bottom()
    ax.spines['top'].set_visible(False)
    ly = len(all_benchmarks_list)
    xticks = np.arange(1, ly + 1)
    # ax.bar(xticks, y, align='center')
    c_witdh = 0
    rects = []
    rects_s = []
    for s in interpreter_list:
        if s not in benchmarks:
            continue

        r = ax.bar( xticks + c_witdh, benchmarks[s],  witdh, align='center',
                    # color=colors[col],colors[x[tick-1].split('\n')[0]]
                    color=color_hatch[s][0], hatch=color_hatch[s][1])
        rects += [r]
        rects_s += [s]
        c_witdh += witdh

    ax.set_xticks(xticks + c_witdh/2.3)

    if small:
        ax.set_xticklabels(all_benchmarks_list, fontsize=14)
    else:
        ax.set_xticklabels(all_benchmarks_list, fontsize=17)

    ax.set_yscale('log', basey=2)
    (y_bottom, y_top) = ax.get_ylim()
    y_height = y_top - y_bottom
    y_height = np.log2(y_height)

    def autolabel(rects, y_height):
        for rect in rects:
            height = rect.get_height()
            p_height = np.log2(height) / y_height
            max_hight = 0.90 if small else 0.90
            if p_height > max_hight:
                label_rotation ='horizontal'
            # elif rect.get_x() > (ly - 3) and p_height > 0.50:
            #     label_rotation ='horizontal'
            else:
                label_rotation ='vertical'

            if small:
                fontsize='small'
            else:
                fontsize='large'

            ax.text( rect.get_x() + rect.get_width()/2.,
                     1.05*height,
                     '%.1f' % height,
                     ha='center',
                     va='bottom',
                     fontsize=fontsize, # fontsize='medium'
                     fontweight='bold',
                     rotation=label_rotation)

    for r in rects:
        autolabel(r, y_height)

    if small:
        ax.legend(rects, rects_s, fontsize='large', ncol=3,
                  bbox_to_anchor=(0., 1.02, 1., .102), loc=3, mode="expand")
    else:
        ax.legend(rects, rects_s, fontsize='large')

    ax.set_xlim(.7, ly + 1)
    ax.yaxis.grid(True)

    ax.set_ylabel("Speedup", fontsize='large')


def reorder_paramters(all_benchmarks_list):
    for _type in all_benchmarks_list:
        bench_params = benchmarks_list[_type][1]
        for _timing in all_benchmarks_list[_type]:
            for _bench in all_benchmarks_list[_type][_timing]:
                if isinstance(all_benchmarks_list[_type][_timing][_bench], list):
                    _temp = ['$REMOVEME$' for i in range(0,len(bench_params[_bench]), 2)]
                    for _param in all_benchmarks_list[_type][_timing][_bench]:
                        _temp[bench_params[_bench].index(_param) / 2] = _param
                    while '$REMOVEME$' in _temp : _temp.remove('$REMOVEME$')
                    all_benchmarks_list[_type][_timing][_bench] = _temp
    return all_benchmarks_list

def pre_process_plot(benchmarks, all_benchmarks_list):
    r_benchmarks = {}
    r_benchmarks_list = {}
    is_bench_list_complete = False
    for _interp in benchmarks:
        if _interp not in r_benchmarks:
            r_benchmarks[_interp] = []
            r_benchmarks_list = []
        for _bench in all_benchmarks_list:
            c_bench_list = []
            if isinstance(all_benchmarks_list[_bench], list):
                idx_bench = int( len(all_benchmarks_list[_bench]) / 2 )
                _bench_params = all_benchmarks_list[_bench]
                for idx in range(len(_bench_params)):
                    _param = _bench_params[idx]
                    if _bench not in benchmarks[_interp] or _param not in benchmarks[_interp][_bench]:
                        r_benchmarks[_interp] += [0.01]
                    else:
                        r_benchmarks[_interp] += [benchmarks[_interp][_bench][_param]]

                    c_bench_list += [ _param if idx != idx_bench else (_param + '\n' + _bench)]
            else:
                if _bench not in benchmarks[_interp]:
                    r_benchmarks[_interp] += [0.01]
                else:
                    r_benchmarks[_interp] += [benchmarks[_interp][_bench]]
                c_bench_list += [_bench]
            if not is_bench_list_complete:
                r_benchmarks_list += c_bench_list

    return r_benchmarks, r_benchmarks_list

def process_plot(benchmarks, all_benchmarks_list, interpreter_list, color_hatch_marker, base):
    for _type in benchmarks:
        for _timing in benchmarks[_type]:
            r_benchmarks, r_bench_list = pre_process_plot(benchmarks[_type][_timing], all_benchmarks_list[_type][_timing])
            size = len(r_bench_list)
            size = (max(size * 2, 8), max(size, 4))
            fig = plt.figure(figsize=size) #, dpi=80)
            ax = fig.add_subplot(1, 1, 1)
            width = 1. / (len(interpreter_list) + 1) # +1 for spacing and -1 for base
            plot_bar_speedups(ax, r_benchmarks, r_bench_list, interpreter_list, color_hatch_marker, width)
            ax.set_xlabel("Benchmarks (" + _type + ") (normalized to " + base + ")")
            fig.subplots_adjust(left=0.03)
            fig.savefig(chart_dir + 'benchmarks_' + _type + '_' + _timing + '.png', bbox_inches='tight')
            fig.savefig(chart_dir + 'benchmarks_' + _type + '_' + _timing + '.pdf', format='pdf', bbox_inches='tight')


def do_speedups(benchmarks, base='CPython'):
    for _type in benchmarks:
        for _timing in benchmarks[_type]:
            for _interp in benchmarks[_type][_timing]:
                if _interp == base:
                    continue

                for _bench in benchmarks[_type][_timing][_interp]:
                    if isinstance(benchmarks[_type][_timing][_interp][_bench], dict):
                        for _param in benchmarks[_type][_timing][_interp][_bench]:
                            b = (benchmarks[_type][_timing][ base  ][_bench][_param])
                            s = (benchmarks[_type][_timing][_interp][_bench][_param])
                            b = b if b > 0.001 else 0.001 # in case it was too fast
                            s = s if s > 0.001 else 0.001 # in case it was too fast
                            s = b / s
                            s = float(("%.3f" % s))
                            benchmarks[_type][_timing][_interp][_bench][_param] = s
                    else:
                        b = (benchmarks[_type][_timing][ base  ][_bench])
                        s = (benchmarks[_type][_timing][_interp][_bench])
                        b = b if b > 0.001 else 0.001 # in case it was too fast
                        s = s if s > 0.001 else 0.001 # in case it was too fast
                        s = b / s
                        s = float(("%.3f" % s))
                        benchmarks[_type][_timing][_interp][_bench] = s
            benchmarks[_type][_timing].pop(base)


def do_geomean(benchmarks):
    for _type in benchmarks:
        for _timing in benchmarks[_type]:
            for _interp in benchmarks[_type][_timing]:
                for _bench in benchmarks[_type][_timing][_interp]:
                    if isinstance(benchmarks[_type][_timing][_interp][_bench], dict):
                        for _param in benchmarks[_type][_timing][_interp][_bench]:
                            g = geomean(benchmarks[_type][_timing][_interp][_bench][_param])
                            benchmarks[_type][_timing][_interp][_bench][_param] = g
                    else:
                        g = geomean(benchmarks[_type][_timing][_interp][_bench])
                        benchmarks[_type][_timing][_interp][_bench] = g


def _read_results():
    list_color_hatch_marker =  [
                            ['k' ,        '' ,  's-'],
                            ['#3f3f3f',   '*',  'o-'],
                            ['#999999',   '' ,  '^-'],
                            ['#bababa',   '/',  '*-'],
                            ['#e2e2e2',   '.',  'P-'],
                            ['w',         '' ,  'X-'],
                        ]

    interpreter_list = []
    color_hatch_marker = {}
    ch = 0
    benchmarks = {}
    all_benchmarks_list = {}
    results_list = os.listdir(machine_results_dir)
    for f in sorted(results_list):
        if f == 'machine.json' or not f.endswith('.json'):
            continue

        result_tag = f.replace('.json','').split('-')
        _interp = result_tag[1] # ZipPy
        _ver    = result_tag[0] # version
        _type   = result_tag[2] # normal, micro,..
        _timing = result_tag[3] # peak
        _run    = result_tag[5] # run #
        _commit = ''

        with open(machine_results_dir + '/' + f) as benchmark_file:
            bench_json = json.load(benchmark_file)
            if 'commit_hash' not in bench_json or bench_json['commit_hash'] != commit_hash:
                continue

            if _type not in benchmarks:
                benchmarks[_type] = {}
                all_benchmarks_list[_type] = {}

            if _timing not in benchmarks[_type]:
                benchmarks[_type][_timing] = {}
                all_benchmarks_list[_type][_timing] = {}

            _commit = bench_json['commit_hash']
            _interp = str(bench_json['params']['interpreter'])

            if _interp not in benchmarks[_type][_timing]:
                benchmarks[_type][_timing][_interp] = {}

            for _single_bench in bench_json['results']:
                _sb = str(_single_bench.replace( _type + '.', ''))

                if _sb not in all_benchmarks_list[_type][_timing]:
                    all_benchmarks_list[_type][_timing][_sb] = None

                if isinstance(bench_json['results'][_single_bench], dict):

                    for i in range(len(bench_json['results'][_single_bench]['params'][0])):
                        _param = str(bench_json['results'][_single_bench]['params'][0][i])
                        _time  = bench_json['results'][_single_bench]['result'][i]
                        if _time == None:
                            continue

                        if all_benchmarks_list[_type][_timing][_sb] == None:
                            all_benchmarks_list[_type][_timing][_sb] = []
                        if _param not in all_benchmarks_list[_type][_timing][_sb]:
                            all_benchmarks_list[_type][_timing][_sb] += [_param]

                        _time = float(_time)
                        if _sb not in benchmarks[_type][_timing][_interp]:
                            benchmarks[_type][_timing][_interp][_sb] = {}

                        if _param not in benchmarks[_type][_timing][_interp][_sb]:
                            benchmarks[_type][_timing][_interp][_sb][_param] = []

                        benchmarks[_type][_timing][_interp][_sb][_param] += [_time]
                else:
                    _time  = bench_json['results'][_single_bench]
                    if _time == None:
                        continue

                    _time = float(_time)
                    if _single_bench not in benchmarks[_type][_timing][_interp]:
                        benchmarks[_type][_timing][_interp][_sb] = []

                    benchmarks[_type][_timing][_interp][_sb] += [_time]


            if _interp not in interpreter_list:
                interpreter_list += [_interp]
                color_hatch_marker[_interp] = list_color_hatch_marker[ch]
                ch += 1

        if debug:
            print("{0}: {1} -- type: {2}  timing: {3} --run {4}  --commit {5}".format(_interp, _ver, _type, _timing, _run, _commit))

    return interpreter_list, color_hatch_marker, benchmarks, reorder_paramters(all_benchmarks_list)

def _asv_chart(args):
    if importerror:
        mx.abort("numpy, matplotlib, or functools library is missing.")
    base = 'CPython'
    try:
        idx = args.index("--")
        args = args[:idx]
    except ValueError:
        pass

    parser = ArgumentParser(
        prog="mx asv-chart",
        add_help=False,
        usage="mx asv-chart <options>",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "--base", nargs="?", default=None,
        help="Select base benchmark.")
    parser.add_argument(
        "--scales", action="store_true", default=None,
        help="Generate scales charts all parametized benchmarks.")
    parser.add_argument(
        "-h", "--help", action="store_true", default=None,
        help="Show usage information.")
    args = parser.parse_args(args)

    if args.base:
        base = args.base

    if not exists(chart_dir):
        os.mkdir(chart_dir)

    interpreter_list, color_hatch_marker, benchmarks, all_benchmarks_list = _read_results()
    interpreter_list.remove(base)
    do_geomean(benchmarks)
    do_speedups(benchmarks)
    process_plot(benchmarks, all_benchmarks_list, interpreter_list, color_hatch_marker, base)
    if args.scales:
        plot_scales(benchmarks, all_benchmarks_list, color_hatch_marker)

mx.update_commands(_suite, {
    'asv-chart' : [_asv_chart, 'Generate chart for benchmarked results.'],
})
