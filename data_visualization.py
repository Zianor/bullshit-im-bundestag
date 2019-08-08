import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def create_heatmap(dict_parties, label):
    # convert nested dict to dataframe using pandas
    df = pd.DataFrame.from_dict(dict_parties).transpose()
    df = df.reindex(sorted(df.columns), axis=1)

    sns.set(font_scale=0.8)

    ax = sns.heatmap(df, cmap='Blues', annot=True, fmt='.1f')
    plt.title(f'{label} von ... für ...\n\n')
    plt.show()


def visualize_distribution_self_other(dict_parties, label):
    df = pd.DataFrame.from_dict(dict_parties)
    df = df.reindex(sorted(df.columns), axis=1)

    sns.set(font_scale=0.8)

    # TODO: search better visual representation (with self and other as stacked bar plot)
    ax = sns.barplot(data=df)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    plt.tight_layout()
    plt.title(f'{label}')
    plt.show()


if __name__ == "__main__":
    pass
