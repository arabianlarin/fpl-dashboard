import pandas as pd
import duckdb
import plotly.express as px
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import ipywidgets as widgets
from PIL import Image
from IPython.display import display, clear_output
from ipywidgets import interact, Dropdown, Output, VBox, HBox
from sklearn.preprocessing import MinMaxScaler
import fpl_api as fa
from datasets import get_dataset, get_player_data

