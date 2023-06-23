# IMPORTS
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import textalloc as ta
import numpy as np
from PIL import Image

# CONSTANTS
BACKGROUND_COLOR = "#15141b"
PRIMARY_COLOR = "#ffffff"

FONT_FAMILY = "sans-serif"

MAXIMUM_MINUTES = 5310

# DATA FETCHING
# Setting up HTTP header
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}

# Fetching the actual data from the web
page = "https://www.transfermarkt.com/fc-barcelona/leistungsdaten/verein/131/reldata/%262022/plus/1"
pageTree = requests.get(page, headers = headers)
pageSoup = BeautifulSoup(pageTree.content, "html.parser")

# DATA PROCESSING
# Extract the table of players from fetched html
player_table = pageSoup.find("table", {"class": "items"}).find("tbody")

# Extract player names
player_names = np.array([x.find("a").text for x in player_table.find_all(lambda tag: tag.name == "span" and tag.get("class") == ["hide-for-small"])])

# Extract player minutes
player_minutes = np.array([0 if (x.text == "Not used during this season") else int(x.text.replace("'", "").replace(".", "")) for x in player_table.find_all(lambda tag: tag.name == "td" and (tag.get("class") == ["rechts"] or tag.get("colspan") == "10"))])

# Extract player ages
player_ages = np.array([int(item.find("td", {"class": "zentriert", "title": False}).text) for item in player_table.find_all("tr") if item.find("td", {"class": "zentriert", "title": False}) is not None])

# Indexing to remove players with zero minutes
valid_indices = player_minutes != 0

player_ages = player_ages[valid_indices]
player_minutes = player_minutes[valid_indices]
player_names = player_names[valid_indices]

# Storing the min and max age from the dataset for later use
minimum_age = np.amin(player_ages)
maximum_age = np.amax(player_ages)

# GRAPH
# Creating the plot area
fig, ax = plt.subplots()
ax2 = ax.twinx()

# Setting up graph global defaults
fig.set_size_inches(16, 9.5)

fig.set_facecolor(BACKGROUND_COLOR)
fig.set_edgecolor(PRIMARY_COLOR)
ax.set_facecolor(BACKGROUND_COLOR)

plt.rc("xtick", labelsize = 12)
plt.rc("ytick", labelsize = 12)

# Setting up spine colors
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_color(PRIMARY_COLOR)
ax.spines["left"].set_color(PRIMARY_COLOR)

ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["bottom"].set_color(PRIMARY_COLOR)
ax2.spines["left"].set_color(PRIMARY_COLOR)

# Setting up ticks color
ax.tick_params(axis = "x", colors = PRIMARY_COLOR, size = 8, labelsize = 13)
ax.tick_params(axis = "y", colors = PRIMARY_COLOR, size = 8, labelsize = 13)
ax2.tick_params(axis = "y", colors = PRIMARY_COLOR, size = 8, labelsize = 13)

# Setting up graph (sub)title
plt.suptitle("PLAYERS' PLAYING TIME IN FC BARCELONA", y = 0.969, fontsize = 20, fontweight = "bold", family = FONT_FAMILY, color = PRIMARY_COLOR)
plt.text(0.5, 1.055, "2022/2023 Season | All competitions", fontsize = 15, transform = plt.gca().transAxes, fontweight = "regular", family = FONT_FAMILY, color = PRIMARY_COLOR, ha = "center", va = "center")

# Setting up axes values and their respective labels
plt.xticks(range(minimum_age, maximum_age + 1), color = PRIMARY_COLOR)
plt.yticks(range(0, MAXIMUM_MINUTES + 1, 500), color = PRIMARY_COLOR)
ax2.set_yticks([0, MAXIMUM_MINUTES * 0.25, MAXIMUM_MINUTES * 0.5, MAXIMUM_MINUTES * 0.75, MAXIMUM_MINUTES])

ax2.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], color = PRIMARY_COLOR)

# Setting up axes labels
ax.set_xlabel("Age", color = PRIMARY_COLOR, family = FONT_FAMILY, fontweight = "bold", fontsize = 15, labelpad = 14)
ax.set_ylabel("Minutes played", color = PRIMARY_COLOR, family = FONT_FAMILY, fontweight = "bold", fontsize = 15, labelpad = 14)
ax2.set_ylabel("% of minutes played", color = PRIMARY_COLOR, family = FONT_FAMILY, fontweight = "bold", fontsize = 15, rotation = 270, labelpad = 14)

# Setting up margins
ax.set_xmargin(0.04)
ax.set_ymargin(2500)

# Setting up axes limits
ax.set_ylim(top = MAXIMUM_MINUTES)
ax2.set_ylim(ax.get_ylim())

# Setting up background spans
ax.axvspan(minimum_age, 23, facecolor = "green", alpha = 0.35, label = "YOUTH")
plt.text(19.15, MAXIMUM_MINUTES / 2, "YOUTH", fontsize = 50, rotation = 90, color = PRIMARY_COLOR, alpha = 0.35, ha = "center", va = "center", fontweight = "bold")

ax.axvspan(24, 29, facecolor = "red", alpha = 0.35, label = "PEAK")
plt.text((24 + 29) / 2, MAXIMUM_MINUTES / 2, "PEAK", fontsize = 50, rotation = 90, color = PRIMARY_COLOR, alpha = 0.35, ha = "center", va = "center", fontweight = "bold")

ax.axvspan(30, maximum_age, facecolor = "yellow", alpha = 0.35, label = "EXPERIENCE")
plt.text((30 + maximum_age) / 2, MAXIMUM_MINUTES / 2, "EXPERIENCE", fontsize = 50, rotation = 90, color = PRIMARY_COLOR, alpha = 0.35, ha = "center", va = "center", fontweight = "bold")

# Setting up scatter grids
ax.set_axisbelow(True)
ax.xaxis.grid(color = "gray", linestyle = "dashed")

ax2.set_axisbelow(True)
ax2.yaxis.grid(color = "gray", linestyle = "dashed")

# Adding logo
plt.figimage(Image.open("logo.png").resize((100, 100), Image.LANCZOS), xo = 17, yo = -1)

# Adding data source text
plt.text(0.84, -0.095, "Source:", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "left", va = "center", color = PRIMARY_COLOR, fontweight = "regular", fontsize = 12)
plt.text(1.0, -0.095, "Transfermarkt", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "right", va = "center", color = PRIMARY_COLOR, fontweight = "bold", fontsize = 12)

# Scatter the data
plt.scatter(player_ages, player_minutes, color = PRIMARY_COLOR, s = 75)

# Label the data
text_list = player_names[np.arange(len(player_names))]
ta.allocate_text(fig, ax, player_ages, player_minutes, text_list, x_scatter = player_ages, y_scatter = player_minutes, family = FONT_FAMILY, textcolor = PRIMARY_COLOR, textsize = 13, linecolor = PRIMARY_COLOR, fontweight = 500)

# Show the graph
plt.show()
