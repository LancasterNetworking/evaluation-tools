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

tableau = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

for i in range(len(tableau)):
    r, g, b = tableau[i]
    tableau[i] = (r / 255., g / 255., b / 255.)


def create_line_graph(name, lines, xlabel, ylabel, legend=True, legend_loc=0):
    plt.clf()

    plt.figure(figsize=(10.00, 4.00))
    plt.tight_layout()
    for idx, line in enumerate(lines):
        print line.label
        c= tableau[idx % len(tableau)]
        t, = plt.plot(line.points, label=line.label, color=c)

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    xaxis = max([len(l.points) for l in lines])
    print 'x-axis: ' + str(xaxis)
    plt.xlim([min([0] + [xaxis]), xaxis])
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
        labels=None, legend_loc=0, order_by=None, outname=None):
    results = {}
    lines = []

    duplicates_exist = lambda x: False if len(x) == len(set(x)) else True

    if duplicates_exist(keys):
        raise Exception('Duplicate keys found')

    if labels is not None:
        if duplicates_exist(labels):
            raise Exception('Duplicate labels found')

    if labels is not None and len(keys) != len(labels):
        raise Exception('keys and labels lengths did not match.')

    for k in keys:
        results[str(k)] = []

    ordering = None if order_by is None else lambda k: int(k[order_by])

    with open(csvname, 'rb') as f:
        reader = csv.DictReader(f)
        for row in sorted(reader, key=ordering):
            for k in results.keys():
                results[k].append(row[k])

    for idx, key in enumerate(keys):
        if labels:
            lines.append(LineGraph(results[key], labels[idx]))
        else:
            lines.append(LineGraph(results[key], str(key)))

    name = ''
    if outname is None:
        name = csvname.replace('.csv', '')
    else:
        name = outname

    create_line_graph(name, lines, xlabel, ylabel,
        legend=legend, legend_loc=legend_loc)
