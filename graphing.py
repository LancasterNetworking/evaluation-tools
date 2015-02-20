import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv

LEGEND_FONT_SIZE = 12
LEGEND_COLUMN_SPACING = 0.5
LEGEND_ALPHA = 0.2


class LineGraph(object):

    def __init__ (self, points, label):
        self.points = points
        self.label = label


def create_line_graph(name, lines, xlabel, ylabel, legend=True, legend_loc=0):
    plt.clf()

    for line in lines:
        print line.label
        t, = plt.plot(line.points, label=line.label)

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    xaxis = max([len(l.points) for l in lines])
    print 'x-axis: ' + xaxis
    plt.xlim([min([0] + xaxis), max(xaxis)])
    if legend:
        legend = plt.legend(loc=legend_loc,
            prop={'size':LEGEND_FONT_SIZE},
            fancybox=True,
            ncol=3,
            columnspacing=LEGEND_COLUMN_SPACING)
        legend.get_frame().set_alpha(LEGEND_ALPHA)
    plt.savefig(name + '.pdf', format='pdf')


def create_line_graph_from_csv(
        csvname, keys, xlabel, ylabel, legend=True,
        labels=None, legend_loc=0, order_by=None):
    results = {}
    lines = []

    duplicates_exist = lambda x: False if len(x) == len(set(x)) else True

    if duplicates_exist(keys):
        raise Exception('Duplicate keys found')

    if duplicates_exist(labels):
        raise Exception('Duplicate labels found')

    if labels is not None and len(keys) != len(labels):
        raise Exception('keys and labels lengths did not match.')

    for k in set(keys):
        results[str(k)] = []

    ordering = None if order_by is None else lambda k: int(k[order_by])

    with open(csvname, 'rb') as f:
        reader = csv.DictReader(f)
        for row in sorted(reader, key=ordering):
            for k in results.keys():
                results[k].append(row[k])

    for idx, key in enumerate(results.keys()):
        if labels:
            lines.append(LineGraph(results[key], labels[idx]))
        else:
            lines.append(LineGraph(results[key], str(key)))

    name = csvname.replace('.csv', '')
    create_line_graph(name, lines, xlabel, ylabel,
        legend=legend, legend_loc=legend_loc)
