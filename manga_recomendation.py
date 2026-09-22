#**********************************************************************
# Author: Scott usher
# Date Created: 9/20/2026
# Purpose: This file is an interactable user interface for a manga recomendation system in the file recomendation_processing.
#
#
#**********************************************************************



import streamlit as st
import json
import os
import sys
import time

from recomendation_processing import manga_recomendation


#***********************************************
# List of functions
#***********************************************

#**********************************************************************
# Purpose: ensuring the data is loaded even if the code is in a pyinstaller exe
#
# Precondition: is given a valid json
#               
# Postcondition: returns a path to access the json data even if it is in an exe 
#
#***********************************************************************
def resource_path(filename):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, filename)


#**********************************************************************
# Purpose: Display genre tags
#
# Precondition: is passed the name of a manga that exists in the data
#               
# Postcondition: displays each tag sequentialy in a html span style (it goes the width of whatever container it is in if it can) 
#
#***********************************************************************
def display_genres(manga):
    genres = st.session_state["filter_manga"][manga]

    genre_html = '<div class="genre-container">'

    for code in genres:
        genre = st.session_state["genre_translation"][str(code)]

        genre_html += f'<span class="genre-tag">{genre}</span>'

    genre_html += '</div>'

    st.markdown(
        genre_html,
        unsafe_allow_html=True
    )

#**********************************************************************
# Purpose: creates a button that whn pressed adds a manga with a rating to the selected manga dictionary
#
# Precondition: there is a selected manga and this function has been passed a rating for it
#               
# Postcondition: adds selected manga to selected manga dictionary if it does not exist in it yet. else warns the program user of such
#
#***********************************************************************
def add_manga_button(score):
    if st.button("Add Selected manga with selected score"):

        if "selected_manga_dict" not in st.session_state:
            st.session_state["selected_manga_dict"] = {}

        selected_manga = st.session_state["selected_manga"]

        already_added = any(
            manga == selected_manga
            for manga in st.session_state["selected_manga_dict"]
        )

        if not already_added:

            st.session_state["selected_manga_dict"][selected_manga] = score


            st.success(f"{selected_manga} added!")

        else: 
            st.warning("This manga has already been added.")


#**********************************************************************
# Purpose: adding functionality to 18+ content toggle to ensure the program user is above age
#
# Precondition: the toggle position is changed
#               
# Postcondition: turns off toggle or changes session state to trigger a request to verifiy their age 
#
#***********************************************************************
def toggle_feature_18():

    if st.session_state["18+_toggle"]:

        # Don't enable yet
        st.session_state["18_confirm_enable"] = True

    # User turned feature OFF
    else:

        st.session_state["18+_content_enabled"] = False
        st.session_state["18_confirm_enable"] = False


#**********************************************************************
# Purpose: setting session state for when 18+ confirmation is denied
#
# Precondition: adult content has been toggled on and 18+ verification has been denied
#               
# Postcondition: sets relavent session states to flase
#
#***********************************************************************
def no_confirm():

    st.session_state["18+_toggle"] = False
    st.session_state["18+_content_enabled"] = False
    st.session_state["18_confirm_enable"] = False


#**********************************************************************
# Purpose: setting session state for when 18+ confirmation is confirmed
#
# Precondition: adult content has been toggled on and 18+ verification has been confirmed
#               
# Postcondition: sets 18+ content to enabled. sets the 18+ confirmation to false as it has now been enabled and no longer needs to be confirmed
#
#***********************************************************************
def yes_confirm():

    st.session_state["18+_content_enabled"] = True
    st.session_state["18_confirm_enable"] = False


#**********************************************************************
# Purpose: displaying manga selected by the product user
#
# Precondition: a manga has been added to the selected manga dictionary 
#               
# Postcondition: displays the selected manga's name image tags and button to remove the manga from the selceted manga dict
#
#***********************************************************************
def display_selected_manga(selected_manga_dict, manga_per_row=9):

    columns = st.columns(manga_per_row)

    for i, (manga, score) in enumerate(selected_manga_dict.items()):

        with columns[i % manga_per_row]:

            st.image(
                st.session_state["manga_data"][manga][1],
                width = "stretch"
            )
            st.markdown(f"#### {manga}")
            st.markdown(f"#### rated: {score}")

            display_genres(manga)
            st.write("\n")
            if st.button(
                "✕ Remove",
                key=f"remove_{manga}"
            ):

                st.session_state["selected_manga_dict"].pop(manga)
                st.rerun()


#**********************************************************************
# Purpose: displaying the recomendations based on the users selected manga
#
# Precondition: button to search for similar manga has been pressed 
#               
# Postcondition: displays 50 manga including their, name, genres, and a button to go to their section in myanimelist.com which holds more information.  
#                the display also includes next 50 and previous 50 which makes the display show the next 50 manga or the previous 50 manga in relation to the current 50 manga that are shown
#                If there are no recomendations in recomendation list it displays nothing. Will show manga half pages of manga if at the end of the recomendation list as it should.
#
#***********************************************************************
def display_recommendations(recommendations, width = 8):
    
    st.write("Recomendation Count: ", len(recommendations))

    start = st.session_state.recommendation_page * 50
    end = start + 50

    current_manga = recommendations[start:end]

    col1, col2, col3 = st.columns([1,1,11])
    with col1:
        if st.session_state.recommendation_page > 0:
            if st.button(f" Previous 50"):
                st.session_state.recommendation_page -= 1
                st.rerun()
    with col2:
        if end < len(recommendations):
            if st.button(f" Next 50 "):
                st.session_state.recommendation_page += 1
                st.rerun()


    for row_start in range(0, len(current_manga), width):

        row = current_manga[row_start:row_start + width]

        columns = st.columns(width)

        for i, manga in enumerate(row):
            with columns[i]:

                with st.container(border=True):
                    st.image(
                        st.session_state["manga_data"][manga][1],
                        width = "stretch"
                    )
                    st.markdown(f"#### {manga}")

                    url = "https://myanimelist.net/" + st.session_state["manga_data"][manga][2]

                    st.link_button(
                        "More Info",
                        url
                    )
                    display_genres(manga)
                    st.markdown('<p style="font-size:5px;">     </p>',    unsafe_allow_html=True)


    col1, col2, col3 = st.columns([1,1,11])
    with col1:
        if st.session_state.recommendation_page > 0:
            if st.button(f"Previous 50"):
                st.session_state.recommendation_page -= 1
                st.rerun()
    with col2:
        if end < len(recommendations):
            if st.button(f"Next 50 "):
                st.session_state.recommendation_page += 1
                st.rerun()


#*****************************
# Runtime Initialization
#*****************************
runtime_dir = os.environ.get("APP_RUNTIME_DIR")

if runtime_dir:
    heartbeat_file = os.path.join(runtime_dir, "heartbeat")

    try:
        os.utime(heartbeat_file, None)
    except FileNotFoundError:
        with open(heartbeat_file, "w"):
            pass


#*****************************
# Load data
#*****************************
if "global_std" not in st.session_state:
    with open(resource_path("datalist.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

        st.session_state["manga_first_collection"] = data["manga_first_collection"]
        st.session_state["user_first_collection"] = data["user_first_collection"]
        st.session_state["manga_data"] = data["manga_data"]
        st.session_state["manga_genres"] = data["manga_genres"]
        st.session_state["genre_translation"] = data["genre_translation"]
        st.session_state["global_average"] = data["global_average"]
        st.session_state["global_std"] = data["global_std"]


#*******************************
# Page Configuration
#*******************************
st.set_page_config(
    page_title="Manga Recomender",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#*******************************
# Initial state
#*******************************

if "18+_content_enabled" not in st.session_state:
    st.session_state["18+_content_enabled"] = False

if "18+_toggle" not in st.session_state:
    st.session_state["18+_toggle"] = False

if "18_confirm_enable" not in st.session_state:
    st.session_state["18_confirm_enable"] = False
    
if "suggestive_content_enabled" not in st.session_state:
    st.session_state["suggestive_content_enabled"] = False
    
if "filter_manga" not in st.session_state:
    st.session_state["filter_manga"] = {}
    
if "filter_genres" not in st.session_state:
    st.session_state["filter_genres"] = []

if "recommendation_page" not in st.session_state:
    st.session_state.recommendation_page = 0

if "filtered_recomendations" not in st.session_state:
    st.session_state["filtered_recomendations"] = []

filter_genres = []
search_filter_parity = True

#*******************************
# Filtered state
#*******************************

if st.session_state["18+_content_enabled"] == False:
    filter_genres.extend([49, 12])

if st.session_state["suggestive_content_enabled"] == False:
    filter_genres.append(9)

if "english_jp" not in st.session_state:
    st.session_state["english_jp"] = {}



#**********************************************************************
# Purpose: filtering manga based on session_state filters
#
# Precondition: a filter has been changed or it is first initialization
#               
# Postcondition: sets session_state filter_manga to hold all manga which qualify through the filters
#                sets session_state filter_genres to the same as the filtered genre making changes in filter state detectable saving on processing time when filters do not change
#
#***********************************************************************
if filter_genres != st.session_state["filter_genres"]:


    #removing manga from selected manga when filters change
    if "selected_manga_dict" in st.session_state:

        remove = []
        for manga in st.session_state["selected_manga_dict"]:
            for genre in st.session_state["manga_genres"][manga]:

                if genre in filter_genres:
                    remove.append(manga)

        for manga in remove:
            st.session_state["selected_manga_dict"].pop(manga)


    search_filter_parity = False

    filter_manga = {}
    english_jp = {}
    add = True
    st.session_state["filter_genres"] = filter_genres
    
    for manga in st.session_state["manga_genres"]:
        add = True

        for genre in filter_genres:
            if genre in st.session_state["manga_genres"][manga]:

                add = False
                break # break if a manga witha invalid tag is found

        if add == True:
            filter_manga[manga] = st.session_state["manga_genres"][manga]

            if st.session_state["manga_data"][manga][3] != manga:
                english_jp[f"{manga} | {st.session_state["manga_data"][manga][3]}"] = manga
            else:
                english_jp[manga] = manga

    st.session_state["english_jp"] = english_jp
    st.session_state["filter_manga"] = filter_manga
        


#*******************************
# Title
#*******************************


col1, col2 = st.columns([3,1])
with col1:
    st.title("Manga Recommendation System")
    st.write("Search for manga, or other Webcomics give them a rating add them to a list, and search for recommendations.")
with col2:
    st.write("")
    st.write("")
    st.write("You should shut down the system before leaving")
    if st.button("Exit Application"):

        shutdown_file = os.path.join(
            runtime_dir,
            "shutdown"
        )
    
        with open(shutdown_file, "w") as f:
                f.write("shutdown")
    
        st.success("Application shutting down...")
        st.stop()




st.markdown("""
<style>
.genre-container {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 6px;
}
.genre-tag {
    padding: 5px 10px;
    border: 1px solid gray;
    border-radius: 12px;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)


selected_manga = st.selectbox(
    "Search for a Manga",
    options = st.session_state["english_jp"].keys(),
    index = None,
    placeholder = "Start typing a manga name..."
)


st.markdown(
    '<span style="font-size: 16px;">I recomend highlighting the existing text and typing the next manga name when searching a new manga (less latency)</span>',
    unsafe_allow_html=True
)


#**********************************************************************
# Purpose: displays information for the current selected manga
#
# Precondition: a manga is selected from the select box 
#               
# Postcondition: displays manga genres, name, image, a link to myanimelist for more information, and a slider to use to rate the manga. 
#                additionaly displays a button to add said manga to the selection dictionary
#
#***********************************************************************
if selected_manga:

    selected_manga = st.session_state["english_jp"][selected_manga]

    col1, col2, col3, col4 = st.columns([2,5.4,3,3.5])

    with col1:
        st.image(st.session_state["manga_data"][selected_manga][1], width="stretch")
    with col2:
        st.write(f"{selected_manga}")
        display_genres(selected_manga)
        st.session_state["selected_manga"] = selected_manga
        st.write("\n")

        score = st.slider(
        "Rate this manga",
        min_value=1,
        max_value=10,
        value=5,
        step=1
    )
    with col3:
        url = "https://myanimelist.net/" + st.session_state["manga_data"][selected_manga][2]
        st.link_button(
            "View Manga information in MAL",
            url
        )

        st.write("\n")
        add_manga_button(score)


#**********************************************************************
# Purpose: displays optional toggles to show mature tags
#
# Precondition: visuals change based on what toggles are toggled
#               
# Postcondition: Displays a UI showing toggles which can add or remove manga from the dictionary of manga which can be used in suggesting mangas to the user
#
#***********************************************************************
with st.sidebar:

    st.header("⚙️ Settings")
    
    st.markdown(
    '<span style="font-size: 22px; color: red;">Disclaimer</span><br><span style="font-size: 15px;">Some manga have mature content without having tags to filter them by, I am not responsible for what you decide to read.</span>',
    unsafe_allow_html=True
)


    st.toggle(
        "Enable Adult Content",
        key = "18+_toggle",
        on_change = toggle_feature_18
    )

        # User is trying to turn the feature ON
    if st.session_state["18_confirm_enable"] and not st.session_state["18+_content_enabled"]:

        st.warning("Are you legaly an adult in your country?")

        col1, col2 = st.columns(2)

        with col1:

            st.button(
                "Yes",
                key="yes_button",
                on_click=yes_confirm
            )

        with col2:

            st.button(
                "No",
                key="no_button",
                on_click=no_confirm
                #on_change=bomb the emabasy
            )

    normal_toggle = st.toggle(
        "Enable Suggestive Content",
        value = False,
        key = "suggestive_content_enabled"
    )


#**********************************************************************
# Purpose: displays button to search for similar manga and create the recomendation list
#
# Precondition: a manga has been added at least once to the selected manga dictionary, 
#               
# Postcondition: creates a list of recomended manga if the button is pressed
#
#***********************************************************************
if "selected_manga_dict" in st.session_state:

    col1, col2 = st.columns([1,4])
    with col1:
        st.subheader("Selected Manga")
    
        if st.button("Click to search for similar manga"):

            search_filter_parity = False
            st.session_state["recomendation_list"] = manga_recomendation(st.session_state["selected_manga_dict"], st.session_state["manga_first_collection"],
                                                                         st.session_state["user_first_collection"], st.session_state["manga_data"], 
                                                                         st.session_state["global_average"] , st.session_state["global_std"])
    with col2:
        if "recomendation_list" in st.session_state:
            st.write("\n")
            st.write("\n")
            st.warning(f"##### Scroll down to see recomendations")

    display_selected_manga(st.session_state["selected_manga_dict"], 9)



#**********************************************************************
# Purpose: displays recomended manga
#
# Precondition: a recomendation list exists and if a filter has been changed then filters the recomendations again to remove or add manga based on filters 
#               
# Postcondition: displays manga recomendations which pass through the filters and enables user to traverse the recomendations
#
#***********************************************************************
if "recomendation_list" in st.session_state:
    if search_filter_parity == False:
    
        st.session_state["filtered_recomendations"] = []
        st.session_state.recommendation_page = False

        for key, manga in st.session_state["recomendation_list"].items():

            if key in st.session_state["filter_manga"]:

                st.session_state["filtered_recomendations"].append(key)
                
    
    display_recommendations(st.session_state["filtered_recomendations"])