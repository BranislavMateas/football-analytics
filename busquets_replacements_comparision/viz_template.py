# IMPORTS
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from mplsoccer import Radar
from bs4 import BeautifulSoup
import requests
from matplotlib.transforms import Bbox
import numpy as np
import os
import time
import csv
from datetime import datetime

# CONSTANTS
BACKGROUND_COLOR = "#15141b"
PRIMARY_COLOR = "#ffffff"

FONT_FAMILY = "sans-serif"

# FUNCTIONS
def get_years(birthdate):
    return datetime.now().year - datetime.strptime(birthdate, "%B %d, %Y").year

def set_cell_design(table, frame):
    cells = table.get_celld().values()
    for cell in cells:
        cell.set_alpha(0)
        cell.set_fontsize(13)

    table_cells = [table.get_celld()[(0, j)].get_text() for j in range(len(frame.columns))]
    for table_cell in table_cells:
        table_cell.set_fontweight("bold")

def create_comparision(player_data_page, save_path):
    # DATA FETCHING PART
    # Initializing HTTP headers and data_sources
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
    data_pages = ["https://fbref.com/en/players/5ab0ea87/Sergio-Busquets", player_data_page]
    
    # Initializing variables for later processment
    data_frames = []

    min_values = []
    max_values = []

    first_player_name = ""
    first_player_age = 0

    second_player_name = ""
    second_player_age = 0

    for i in range(len(data_pages)):
        # Fetching the actual data from the storage/web
        file_path = "busquets_replacements_comparision/assets/" + data_pages[i].split("/")[-1] + ".html"

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                html = file.read()
        else:
            time.sleep(3)
            html = requests.get(data_pages[i], headers = headers).content
            with open(file_path, 'wb') as file:
                file.write(html)

        pageSoup = BeautifulSoup(html, "html.parser")

        # DATA PROCESSING PART
        player_report = pageSoup.find("table", {"id": "scout_summary_MF"})

        # Processing table headers
        header_row = player_report.find("thead").find("tr")
        table_headers = np.array([th.text for th in header_row.find_all("th")])

        # Processing the table body - Filtering out the rows
        body_rows = player_report.find("tbody").find_all("tr")

        excluded_stats = ["Shots Total", "Non-Penalty Goals", "Non-Penalty xG", "npxG + xAG", "Touches (Att Pen)"]
        filtered_rows = [row for row in body_rows if not any(row_item.text in excluded_stats for row_item in row)]

        # Processing the table body - Creating a DataFrame
        data = np.array([[target.text for target in row.find_all(lambda tag: tag.name == "td" or tag.name == "th")] for row in filtered_rows])
        data = data[data[:, 0] != ""]
        data = [[stat[0], float(stat[1].replace("%", "")), int(stat[2].strip())] for stat in data]

        df = pd.DataFrame(data, columns = table_headers)

        # Processing player names and ages
        player_info = pageSoup.find("div", {"id": "meta"})

        if (i == 0):
            first_player_name = player_info.find("span").text
            first_player_age = get_years(player_info.find("span", {"data-birth": True}).text.strip())
        if (i == 1):
            second_player_name = player_info.find("span").text
            second_player_age = get_years(player_info.find("span", {"data-birth": True}).text.strip())

        # Processing the min and max radar values
        if (i == 0):
            if (not os.path.exists("busquets_replacements_comparision/assets/data.csv")):
                values_links = list(map(lambda x: "https://fbref.com" + x[0], filter(lambda y: y != [], [[td["data-endpoint"] for td in row.find_all("td", {"data-endpoint": True})] for row in filtered_rows])))
                
                for j in range(len(values_links)):
                    time.sleep(3)

                    pageTree = requests.get(values_links[j], headers = headers)
                    pageSoup = BeautifulSoup(pageTree.content, "html.parser")

                    values = pageSoup.find("tbody").find_all("td", {"data-stat": "per90"})
                    min_values.append(float(values[-1].text))
                    max_values.append(float(values[0].text))

                with open("busquets_replacements_comparision/assets/data.csv", "w", newline = "") as file:
                    writer = csv.writer(file)
                    writer.writerows([min_values, max_values])

            else:
                with open("busquets_replacements_comparision/assets/data.csv", "r") as file:
                    reader = csv.reader(file)
                    i = 0
                    for row in reader:
                        sublist = [float(element) for element in row]
                        
                        if (i == 0):
                            min_values = sublist
                        if (i == 1):
                            max_values = sublist

                        i += 1

        # Editing dataframe edge case
        df.at[4, "Statistic"] = " Pass Completion % "

        # Adding dataframe into data_frames array
        data_frames.append(df)

    # VIZ PART
    # Creating the plot area
    fig, (ax1, ax2) = plt.subplots(1, 2)

    # Setting up graph global defaults
    fig.set_size_inches(16, 9.5)
    fig.set_facecolor(BACKGROUND_COLOR)
    fig.set_edgecolor(PRIMARY_COLOR)
    fig.subplots_adjust(left = 0.004, right=1)

    plt.subplots_adjust(wspace=0.1)
    plt.rcParams["text.color"] = PRIMARY_COLOR

    ax2.set_facecolor(BACKGROUND_COLOR)
    ax2.axis("off")

    # Setting up title
    plt.suptitle("BUSQUETS' POTENTIAL REPLACEMENTS COMPARISION", y = 0.969, fontsize = 20, fontweight = "bold", family = FONT_FAMILY, color = PRIMARY_COLOR)

    # LEFT SUBPLOT
    # Scattering the plot on the left subplot
    radar = Radar(num_rings = 6, params = data_frames[0]["Statistic"], min_range = min_values, max_range = max_values)

    # Setting up radar axes
    radar.setup_axis(ax = ax1)

    ax1.set_facecolor(BACKGROUND_COLOR)

    # Rendering radar
    radar.draw_circles(ax = ax1, facecolor = "grey", alpha = 0.1)

    radar.draw_range_labels(ax = ax1, color = "white", alpha = 0.5)
    radar.draw_param_labels(ax = ax1, fontsize = 13, fontweight = "bold", color = PRIMARY_COLOR)

    radar.draw_radar_compare(values = data_frames[0]["Per 90"], compare_values = data_frames[1]["Per 90"], ax = ax1, kwargs_radar = {"facecolor": '#a277ff', "alpha": 0.65}, kwargs_compare = {"facecolor": "#5fffca", "alpha": 0.65})

    # Setting up disclaimer
    plt.text(-0.6, -0.099, "*Player compared to positional peers in\nMen's Big 5 Leagues, UCL, UEL over the last 365 days.", ha = "center", fontweight = "bold", fontsize = 11, family = FONT_FAMILY, transform = plt.gca().transAxes, color = PRIMARY_COLOR, style="italic")

    # RIGHT SUBPLOT
    # Scattering the table on the right subplot
    plt.text(0.42, 0.95, (first_player_name + " (" + str(first_player_age) + ")").upper(), ha = "center", fontweight = "bold", fontsize = 30, family = FONT_FAMILY, transform = plt.gca().transAxes, color = "#a277ff")
    table1 = ax2.table(cellText = data_frames[0].values, colLabels = data_frames[0].columns, cellLoc = "center", bbox = Bbox.from_bounds(0.049, 0.505, 0.8, 0.425))

    table1.auto_set_font_size(False)

    # Setting cell design for table1
    set_cell_design(table1, data_frames[0])

    plt.text(0.42, 0.4, (second_player_name + " (" + str(second_player_age) + ")").upper(), ha = "center", fontweight = "bold", fontsize = 30, family = FONT_FAMILY, transform = plt.gca().transAxes, color = "#5fffca")
    table2 = ax2.table(cellText = data_frames[1].values, colLabels = data_frames[1].columns, cellLoc = "center", bbox = Bbox.from_bounds(0.049, -0.045, 0.8, 0.425))

    table2.auto_set_font_size(False)

    # Setting cell design for table2
    set_cell_design(table2, data_frames[1])

    # Adding logo
    plt.figimage(Image.open("logo.png").resize((100, 100), Image.LANCZOS), xo = 17, yo = -1)

    # Adding data source text
    plt.text(0.95, 0.54, "Source:", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "right", va = "center", color = PRIMARY_COLOR, fontweight = "regular", fontsize = 12, rotation = 270)
    plt.text(0.95, 0.46, "FBref", transform = plt.gca().transAxes, family = FONT_FAMILY, ha = "right", va = "center", color = PRIMARY_COLOR, fontweight = "bold", fontsize = 12, rotation = 270)

    # Save the figure to a custom path
    save_path = save_path + "\\" + save_path.split("\\")[-1] + "_viz.png"
    plt.savefig(save_path)

    # Show the viz
    plt.show()
