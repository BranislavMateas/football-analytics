# IMPORTS
from bs4 import BeautifulSoup
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

# CONSTANTS
BACKGROUND_COLOR = "#15141b"
PRIMARY_COLOR = "#ffffff"

FONT_FAMILY = "sans-serif"

# HELPING FUNCTIONS
def getImage(path):
    return OffsetImage(plt.imread(path), alpha = 1, zoom = 0.225)

# DATA FETCHING
# Setting up HTTP header
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}

# Fetching the actual data from the web
page = "https://fbref.com/en/comps/12/La-Liga-Stats"
pageTree = requests.get(page, headers = headers)
pageSoup = BeautifulSoup(pageTree.content, "html.parser")

# DATA PROCESSING
# Extract the table of club stats from fetched html
clubs_table = pageSoup.find("table", {"id": "results2022-2023121_overall"}).find("tbody")

# Extracting the club names
club_names = np.array([item.find("a").text for item in clubs_table.find_all("td", {"data-stat": "team"}) if item.find("a") is not None])

# Extracting the GF
club_goals_for = np.array([int(item.text) for item in clubs_table.find_all("td", {"data-stat": "goals_for"}) if item is not None])

# Extracting the GA
club_goals_against = np.array([int(item.text) for item in clubs_table.find_all("td", {"data-stat": "goals_against"}) if item is not None])

# GRAPH
# Creating the plot area
fig, ax = plt.subplots(dpi=120)

fig.set_facecolor(BACKGROUND_COLOR)
fig.set_edgecolor(PRIMARY_COLOR)
ax.set_facecolor(BACKGROUND_COLOR)

plt.rc("xtick", labelsize = 9)
plt.rc("ytick", labelsize = 9)

# Setting up spine colors
ax.spines["top"].set_color(PRIMARY_COLOR)
ax.spines["right"].set_color(PRIMARY_COLOR)
ax.spines["bottom"].set_color(PRIMARY_COLOR)
ax.spines["left"].set_color(PRIMARY_COLOR)

# Setting up ticks color
ax.tick_params(axis = "x", colors = PRIMARY_COLOR)
ax.tick_params(axis = "y", colors = PRIMARY_COLOR)

# Setting up title
plt.suptitle("CLUBS' GF AND GA DURING THE 2022/23 LA LIGA SEASON", fontsize = 15, fontweight = "bold", family = FONT_FAMILY, color = PRIMARY_COLOR)

# Setting up axes labels
ax.set_xlabel("Goals for (Attack)", color = PRIMARY_COLOR, family = FONT_FAMILY, fontweight = "bold")
ax.set_ylabel("Goals against (Defense)", color = PRIMARY_COLOR, family = FONT_FAMILY, fontweight = "bold")

# Setting up axes limits
ax.set_ylim(bottom = club_goals_against.min() - 7, top = club_goals_against.max() + 7)

# Setting up section labels
ax.text(club_goals_for.min() - 1.75, club_goals_against.max() + 5, "Poor attack & Poor defense", color = PRIMARY_COLOR, size = "9", fontfamily = FONT_FAMILY, fontweight = 600, ha = "left", va = "center")
ax.text(club_goals_for.min() - 1.75, club_goals_against.min() - 5.25, "Poor attack & Strong defense", color = PRIMARY_COLOR, size = "9", fontfamily = FONT_FAMILY, fontweight = 600, ha = "left", va = "center")
ax.text(club_goals_for.max() + 1.75, club_goals_against.min() - 5.25, "Strong attack & Strong defense", color = PRIMARY_COLOR, size = "9", fontfamily = FONT_FAMILY, fontweight = 600, ha = "right", va = "center")
ax.text(club_goals_for.max() + 1.75, club_goals_against.max() + 5, "Strong attack & Poor defense", color = PRIMARY_COLOR, size = "9", fontfamily = FONT_FAMILY, fontweight = 600, ha = "right", va = "center")

# Adding logo
plt.figimage(Image.open("logo.png").resize((70, 70), Image.LANCZOS), xo = 10, yo = 0)

# Adding data source text
plt.text(0.965, -0.095, "Source:", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "right", va = "center", color = PRIMARY_COLOR, fontweight = "regular", fontsize = 9)
plt.text(1.0, -0.095, "FBref", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "right", va = "center", color = PRIMARY_COLOR, fontweight = "bold", fontsize = 9)

# Plot the data
plt.plot(club_goals_for, club_goals_against, "o")
plt.plot([club_goals_for.mean(), club_goals_for.mean()], [club_goals_against.max(), club_goals_against.min()], linestyle = ":", lw = 1, color = PRIMARY_COLOR)
plt.plot([club_goals_for.min(), club_goals_for.max()], [club_goals_against.mean(), club_goals_against.mean()], linestyle = ":", lw = 1, color = PRIMARY_COLOR)

# Label the data
for i in range(len(club_names)):
    ab = AnnotationBbox(getImage("laliga_teams_22_23_gf_ga_vizz/crests/" + club_names[i] + ".png"), (club_goals_for[i], club_goals_against[i]), frameon = False)
    ax.add_artist(ab)

# Display the vizz
plt.show()
