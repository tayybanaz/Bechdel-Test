import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def func(pct, allvalues):
    absolute = int(pct / 100.*np.sum(allvalues))
    return "{:.1f}%\n({:d} )".format(pct, absolute)

def read_csv():
    df = pd.read_csv('score_info.csv', sep=",",header=None)
    data_array = df.to_numpy()
    print(data_array)
    print(len(data_array))
    # scores can be 0, 1 , 2 , 3
    zero_count, one_count, two_count, three_count = 0, 0, 0, 0
    for data in data_array:
        score_count = data[1] + data[2] + data[3]
        if score_count == 0 :
            zero_count = zero_count + 1
        elif score_count == 1:
            one_count = one_count + 1
        elif score_count == 2:
            two_count = two_count + 1
        elif score_count == 3:
            three_count = three_count + 1
    print(zero_count, one_count, two_count, three_count)

    data = np.array([zero_count, one_count, two_count, three_count])
    labels = ['zero', 'one','two', 'three']
    explode = (0.3, 0.2, 0.1, 0.0)

    colors = ("firebrick", "darkorange", "gold",
              "forestgreen")

    wp = {'linewidth': 1, 'edgecolor': "green"}

    fig, ax = plt.subplots(figsize=(10, 10))
    wedges, texts, autotexts = ax.pie(data,
                                      autopct=lambda pct: func(pct, data),
                                      explode=explode,
                                      labels=labels,
                                      shadow=True,
                                      colors = colors,
                                      startangle=90,
                                      wedgeprops=wp,
                                      textprops=dict(color="black"))

    # Adding legend
    ax.legend(wedges, labels,
              title="total score",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))



    # show plot
    plt.show()

read_csv()