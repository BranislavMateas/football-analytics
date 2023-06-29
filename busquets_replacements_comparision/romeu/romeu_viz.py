# IMPORTS
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

import viz_template

# CREATE VIZZ
viz_template.create_comparision("https://fbref.com/en/players/4b511457/Oriol-Romeu", current_dir)
