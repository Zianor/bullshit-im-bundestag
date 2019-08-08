import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def create_heatmap(dict_parties, label, filename='none'):
    """
    Creates heapmap of the given dictionary and labels it. If a filename is given, it will save it, otherwise it will
    show it
    :param dict_parties: given dictionary
    :param label: name of the heatmap
    :param filename: filename if heapmap should be saved
    """
    # convert nested dict to dataframe using pandas
    df = pd.DataFrame.from_dict(dict_parties).transpose()
    df = df.reindex(sorted(df.columns), axis=1)

    sns.set(font_scale=0.8)

    ax = sns.heatmap(df, cmap='Blues', annot=True, fmt='.1f')
    plt.title(f'{label} von ... für ...\n\n')

    if filename != 'none':
        plt.savefig(filename, quality=95, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def visualize_distribution_self_other(dict_parties, label, filename='none'):
    """
    Visualizes proportion of given dict from self to others. If a filename is given, it will save it, otherwise it will
    show it
    :param dict_parties: given dictionary
    :param label: name of the figure
    :param filename: filename if figure should be saved
    """
    df = pd.DataFrame.from_dict(dict_parties)
    df = df.reindex(sorted(df.columns), axis=1)

    sns.set(font_scale=0.8)

    # TODO: search better visual representation (with self and other as stacked bar plot)
    ax = sns.barplot(data=df)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    plt.tight_layout()
    plt.title(f'{label}')

    if filename != 'none':
        plt.savefig(filename, quality=95, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    pass
