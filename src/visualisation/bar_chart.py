import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objs import Layout
import numpy as np

from src.visualisation.classification_mappings import summit_visualisation_config as summit_config


def count_visits(df: pd.DataFrame, classification: str):
    visited = len(df.loc[(df['latest_visit'].notnull()) & (df[classification] == 1)])
    total = len(df.loc[df[classification] == 1])
    return visited, total


def compute_compleation_report(df: pd.DataFrame) -> pd.DataFrame:
    visited_column = []
    total_column = []
    names = []
    for classification, config in summit_config.items():
        visited, total = count_visits(df, classification)
        names.append(config.name)
        visited_column.append(visited)
        total_column.append(total)

    return pd.DataFrame(index=names,
                        data={'total': total_column,
                              'visited': visited_column})


def plot_compleation_report(df: pd.DataFrame):
    df['visited'] = False
    df.loc[df['latest_visit'].notnull(), 'visited'] = True

    layout = Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig = go.Figure(layout=layout)

    for classification, config in summit_config.items():
        visited, total = count_visits(df, classification)
        left_to_go = total - visited

        customdata = np.array([[config.name, visited, total]])
        hovertemplate = '%{customdata[0]}: %{customdata[1]}/%{customdata[2]}<extra></extra>'

        fig.add_trace(go.Bar(x=[config.name],
                             y=[visited],
                             name=config.name,
                             marker_color=config.color,
                             opacity=1.,
                             customdata=customdata,
                             hovertemplate=hovertemplate,

                             )
                      )

        fig.add_trace(go.Bar(x=[config.name],
                             y=[left_to_go],
                             name=config.name,
                             marker_color=config.color,
                             opacity=.5,
                             customdata=customdata,
                             hovertemplate=hovertemplate,
                             ))

    fig.update_layout(barmode='stack',
                      showlegend=False,
                      title="Compleation Progress",
                      xaxis_title="Summit Classification",
                      yaxis_title="Summit Count",
                      template='plotly_white')

    fig.update_yaxes(
        showline=True,  # add line at x=0
        linecolor='black',  # line color
        linewidth=2.4,  # line size
        ticks='outside',  # ticks outside axis
        mirror=True,  # add ticks to top/right axes
        tickwidth=2.4,  # tick width
        tickcolor='black',  # tick color
    )
    fig.update_xaxes(
        showline=True,
        showticklabels=True,
        linecolor='black',
        linewidth=2.4,
        ticks='outside',
        mirror=True,
        tickwidth=2.4,
        tickcolor='black',
    )

    return fig
