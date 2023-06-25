# IMPORTS
from statsbombpy import sb
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from PIL import Image
import pandas as pd
import os
import json

# CONSTANTS
BACKGROUND_COLOR = "#15141b"
PRIMARY_COLOR = "#ffffff"

FONT_FAMILY = "sans-serif"

DATA_FILE_PATH = "messi_busquets_laliga_passes_viz/passes.csv"

# HELPING FUNCTIONS
def drawPass(row, ax):
    if (row["pass_outcome"] == "Incomplete"):
        color = "#60ffce"
    else:
        color = "#a277ff"

    location = json.loads(row["location"])
    end_location = json.loads(row["pass_end_location"])

    ax.arrow(x = location[0], y = location[1], dx = end_location[0] - location[0], dy = end_location[1] - location[1], head_width = 1, head_length = 1, color = color)

def createPitch(ax):
    # Pitch outline & Centre line
    plt.plot([0, 0], [0, 90], color = PRIMARY_COLOR)
    plt.plot([0, 130], [90, 90], color = PRIMARY_COLOR)
    plt.plot([130, 130], [90, 0], color = PRIMARY_COLOR)
    plt.plot([130, 0], [0, 0], color = PRIMARY_COLOR)
    plt.plot([65, 65], [0, 90], color = PRIMARY_COLOR)
    
    # Left penalty area
    plt.plot([16.5, 16.5], [65, 25], color = PRIMARY_COLOR)
    plt.plot([0, 16.5], [65, 65], color = PRIMARY_COLOR)
    plt.plot([16.5, 0], [25, 25], color = PRIMARY_COLOR)
    
    # Right penalty area
    plt.plot([130, 113.5], [65, 65], color = PRIMARY_COLOR)
    plt.plot([113.5, 113.5], [65, 25], color = PRIMARY_COLOR)
    plt.plot([113.5, 130], [25, 25], color = PRIMARY_COLOR)
    
    # Left 6-yard box
    plt.plot([0, 5.5], [54, 54], color = PRIMARY_COLOR)
    plt.plot([5.5, 5.5], [54, 36], color = PRIMARY_COLOR)
    plt.plot([5.5, 0.5], [36, 36], color = PRIMARY_COLOR)
    
    # Right 6-yard box
    plt.plot([130, 124.5], [54, 54], color = PRIMARY_COLOR)
    plt.plot([124.5, 124.5], [54, 36], color = PRIMARY_COLOR)
    plt.plot([124.5, 130], [36, 36], color = PRIMARY_COLOR)
    
    # Preparing circles
    centreCircle = plt.Circle((65, 45), 9.15, color = PRIMARY_COLOR, fill = False)
    centreSpot = plt.Circle((65, 45), 0.8, color = PRIMARY_COLOR)
    leftPenSpot = plt.Circle((11, 45), 0.8, color = PRIMARY_COLOR)
    rightPenSpot = plt.Circle((119, 45), 0.8, color = PRIMARY_COLOR)
    
    # Drawing circles
    ax.add_patch(centreCircle)
    ax.add_patch(centreSpot)
    ax.add_patch(leftPenSpot)
    ax.add_patch(rightPenSpot)
    
    # Preparing arcs
    leftArc = Arc((11, 45), height = 18.3, width = 18.3, angle = 0, theta1 = 310, theta2 = 50, color = PRIMARY_COLOR)
    rightArc = Arc((119, 45), height = 18.3, width = 18.3, angle = 0, theta1 = 130, theta2 = 230, color = PRIMARY_COLOR)

    # Drawing arcs
    ax.add_patch(leftArc)
    ax.add_patch(rightArc)
    
    # Tidying axes
    plt.axis("off")

# PROCESSING DATA
if os.path.exists(DATA_FILE_PATH):
    all_passes = pd.read_csv(DATA_FILE_PATH)
else:
    # Getting all the Messi's LaLiga match_ids from StatsBomb dataset
    season_ids = np.array([90, 42, 4, 1, 2, 27, 26, 25, 24, 23, 22, 21, 41]) # as Messi's first match with Busquets was in September 2008 against Racing Santander
    match_ids = pd.concat([sb.matches(competition_id = 11, season_id = season_id)["match_id"] for season_id in season_ids])

    # Concating all the passes into one DataFrame and saving it to a CSV file if it does not exist yet
    all_passes = pd.concat([sb.events(match_id = match_id)[(sb.events(match_id = match_id)["type"] == "Pass") & (sb.events(match_id = match_id)["player"] == "Sergio Busquets i Burgos") & (sb.events(match_id = match_id)["pass_recipient"] == "Lionel Andrés Messi Cuccittini")] for match_id in match_ids])
    all_passes.to_csv(DATA_FILE_PATH, index = False)

# VIZ
# Creating figure
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

# Setting up graph global defaults
fig.set_size_inches(14.5, 9.5)

fig.subplots_adjust(left = 0.1185, right = 0.885)

fig.set_facecolor(BACKGROUND_COLOR)
fig.set_edgecolor(PRIMARY_COLOR)

# Setting up margins
ax.set_xmargin(0)
ax.set_ymargin(0)

# Creating pitch
createPitch(ax)

# Creating pass map
all_passes.apply(drawPass, axis = 1, ax = ax)

# Setting up graph (sub)title
plt.suptitle("EVERY BUSQUETS' PASS TO MESSI DURING HIS BARCELONA CAREER", x = 0.5, y = 0.969, fontsize = 20, fontweight = "bold", family = FONT_FAMILY, color = PRIMARY_COLOR)
plt.text(0.5, 1.055, "Seasons from 2008/09 – 2020/21 | LaLiga", fontsize = 15, transform = plt.gca().transAxes, fontweight = "regular", family = FONT_FAMILY, color = PRIMARY_COLOR, ha = "center", va = "center")

# Adding logo
plt.figimage(Image.open("logo.png").resize((100, 100), Image.LANCZOS), xo = 17, yo = -1)

# Adding the data source
plt.text(0.905, -0.0735, "Source:", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "right", va = "center", color = PRIMARY_COLOR, fontweight = "regular", fontsize = 12)
plt.text(1.0, -0.0735, "StatsBomb", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "right", va = "center", color = PRIMARY_COLOR, fontweight = "bold", fontsize = 12)

# Adding legend texts
line1 = plt.Line2D([], [], color="#a277ff", linewidth = 3)
line2 = plt.Line2D([], [], color="#60ffce", linewidth = 3)

plt.legend((line1, line2), ("Successful pass", "Non-successful pass"), loc = "upper left", framealpha = 0, labelcolor = PRIMARY_COLOR, prop = {"family": FONT_FAMILY, "size": 14, "weight": "bold", "style": "italic"})

# Adding informational texts
plt.text(-0.073, 0.5, "PASSES ATTEMPTED\n" + str(all_passes.shape[0]), transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "center", va = "center", color = PRIMARY_COLOR, fontweight = "bold", fontsize = 40, rotation = 90)

condition = all_passes.apply(lambda row: hasattr(row, "pass_outcome") and row["pass_outcome"] == "Incomplete", axis = 1)
non_successful_passes = all_passes[condition]

plt.text(1.07, 0.5, "SUCCESS RATE\n" + "{:.2f}".format((100 - (len(non_successful_passes) / all_passes.shape[0] * 100))) + "%", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "center", va = "center", color = PRIMARY_COLOR, fontweight = "bold", fontsize = 40, rotation = 270)

# Displaying the viz
plt.show()
