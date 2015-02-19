import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LEGEND_FONT_SIZE = 12
LEGEND_COLUMN_SPACING = 0.5
LEGEND_ALPHA = 0.2

class LineGraph(object):

    def __init__ (self, points, label):
        self.points = points
        self.label = label

def create_line_graph(name, lines, xlabel, ylabel, legend_loc=0):
    plt.clf()

    for line in lines:
        t, = plt.plot(line.points, label=line.label)

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.xlim([0, max(len(l.points) for l in lines])
    legend = plt.legend(loc=legend_loc,
        prop={'size':LEGEND_FONT_SIZE},
        fancybox=True,
        ncol=3,
        columnspacing=LEGEND_COLUMN_SPACING)
    legend.get_frame().set_alpha(LEGEND_ALPHA)
    plt.savefig(name + '.pdf', format='pdf')

def create_line_graph_from_csv(csvname, keys, xlabel, ylabel, legend_loc=0 order_by=None):
    results = {}
    lines = []

    for k in set(keys):
        results[str(k)] = []

    ordering = None if order_by is None else lambda k: int(k[order_by])

    with open(csvfile, 'rb') as f:
        reader = csv.DictReader(f)
        for row in sorted(reader, key=ordering):
            for k in results.keys():
                results[k].append(row[k])

    for k in results.keys():
        lines.append(LineGraph(results[k], str(k)))

    name = csvname.replace('.csv', '')
    create_line_graph(name, lines, xlabel, ylabel, legend_loc)
