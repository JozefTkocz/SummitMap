from dataclasses import dataclass


@dataclass
class SummitVisualisationConfig:
    color: str
    name: str


summit_visualisation_config = {
    'W': SummitVisualisationConfig(color='yellow', name='Wainwright'),
    'F': SummitVisualisationConfig(color='lightblue', name='Furth'),
    'D': SummitVisualisationConfig(color='purple', name='Donald'),
    'G': SummitVisualisationConfig(color='green', name='Graham'),
    'C': SummitVisualisationConfig(color='orange', name='Corbett'),
    'M': SummitVisualisationConfig(color='red', name='Munro'),
}
