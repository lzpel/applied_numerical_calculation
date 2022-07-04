import glob
import re
import numpy
import numpy as np


def fetch_path_array(wildcard="./*.html"):
    return glob.glob(wildcard)


def read_html(path_html, flag_year_month):
    result_month = []
    result_year = []
    year_data = []
    year = 0
    with open(path_html, mode="r", encoding="EUC-JP") as f:
        t = f.read()
        t = re.sub(r'\s+(<TD)', r'\1', t)
        for line in t.splitlines():
            if m := re.search(r'(\d+)年　雨量年表', line):
                year = int(m.groups()[0])
            if m := re.search(r'(\d+)月</FONT></TH>', line):
                month = int(m.groups()[0])
                month_data = [float(ms.groups()[0]) for ms in re.finditer(r'size="-1">([\d\.]+)</FONT></TD>', line)]
                if len(month_data) > 30 / 2:
                    result_month.append((year * 100 + month, max(month_data)))
                year_data.extend(month_data)
        if len(year_data) > 365 / 2:
            result_year.append((year, max(year_data)))
        print(result_year)
        print(result_month)
        if flag_year_month:
            return result_year
        else:
            return result_month


def concat_lists(iter_lists):
    return sum(iter_lists, start=[])


def statistics(array, flag_year_month):
    print(len(array))
    avg = np.average(array)
    var = np.var(array)
    print(avg, var)
    a = np.sqrt(6 * var / np.pi ** 2)
    c = avg - 0.5772 * a
    print(a, c, c + 0.5772 * a, (np.pi * a) ** 2 / 6)
    fig, ax = make_figure()
    x_p = lambda p: c - a * np.log(-np.log(p))
    f_x = lambda x: 1 / a * np.exp(-(x - c) / a - np.exp(-(x - c) / a))
    x = list(range(1, 600))
    y = [f_x(i) for i in x]
    ax.plot(x, y)
    ax.set_xlabel('$x$ 24時間降水量[mm]')
    ax.set_ylabel('$f_X(x)$ 確率密度[1]')
    ax.text(1, 1, "$\overline{{x}}={:4.2f}$ $\sigma_x^2={:4.2f}$ $a={:4.2f}$ $c={:4.2f}$".format(avg, var, a, c),
            ha='right', va='bottom', transform=ax.transAxes)
    for year in [2, 10, 100, 200]:
        x = x_p(1 - 1.0 / (year if flag_year_month else year * 12))
        ax.plot([x, x], [min(y), max(y)], label="{}年最大日降水量={}mm".format(year, int(x)), scalex=False)
    ax.legend()
    fig.savefig("sample_{}.pdf".format(flag_year_month))


def make_figure():
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = 'MS Mincho'
    plt.rcParams["font.size"] = 12
    fig = plt.figure()
    ax = fig.add_subplot(111)
    return fig, ax


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    paths = fetch_path_array()
    print(paths)
    for flag_year_month in [True, False]:
        result = concat_lists(read_html(path, flag_year_month) for path in paths)
        if flag_year_month:
            for i in result:
                print("{}&{}\\\\".format(i[0], i[1]))
        else:
            tmp = {}
            for i in result:
                key = int(i[0] / 100)
                tmp.setdefault(key, {})
                tmp[key][i[0] % 100] = i[1]
            for key, value in tmp.items():
                print("{}&{}&{}\\\\".format(key, max(value.values()), ",".join("{}月{}".format(k,v) for k,v in value.items())))
        statistics([i[1] for i in result], flag_year_month)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
