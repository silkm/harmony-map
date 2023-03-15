import folium
from folium.plugins import MarkerCluster, FeatureGroupSubGroup
import pandas as pd
import urllib.request
from os.path import exists
import colorcet


# Read in the data
harmony_data = pd.read_csv("Harmony Day - Interactive Map-MASTER LIST.csv")

# Load locations lookups, trim trailing whitespace
locations = pd.read_csv("locations.tsv", sep='\t')
locations['loc_string'] = locations['loc_string'].str.strip()


# Initialise the map
m = folium.Map(max_bounds=False, tiles=None, location=[0,0], zoom_start=2)
folium.raster_layers.TileLayer(tiles='openstreetmap', name='Questions').add_to(m)

# Create layers. For you to be able to use cluster (to
# prevent points overlaying on top of each other) with
# toggles to turn categories on and off, you must create
# a MarkerCluster and add FeatureSubGroups to it. Marker
# points then get added to the FeatureSubGroups.
marker_cluster = MarkerCluster(control=False, options={'maxClusterRadius':10})
m.add_child(marker_cluster)

# Collect unique questions and make ordered set of groups
question_set = harmony_data.iloc[:, 2].values.flatten().tolist()
unique_questions = sorted(list(set(sum([a.split(',') for a in question_set], []))))
groups = [FeatureGroupSubGroup(marker_cluster, name=a) for a in unique_questions]
for group in groups:
    m.add_child(group)


class Answer:
    """Basic marker object with fixed frame size"""

    def __init__(self, name, loc, coords, question, text, img_name, img_link):
        self.name = name
        self.loc = loc
        self.coords = coords
        self.question = question
        self.text = text
        self.img_name = img_name
        self.img_link = img_link

    def marker(self):
        if self.img_name:
            imgstring = f'<img src="img/{self.img_name}" width="300">'
        else:
            imgstring = ''

        # Select colour by person's row in data
        person_index = harmony_data[harmony_data['Name'] == self.name].index[0]
        person_colour = colorcet.glasbey_dark[person_index]

        htmlcode = f"""
        <div>
        {imgstring}
        <br /><span>
        <b><big>{self.loc}</big></b>
        <br />
        <i>{self.question}</i>
        <br />
        {self.text}
        <br />
        <i>&nbsp&nbsp&nbsp&nbsp- {self.name}</i>
        </span>
        </div>
        """
        # tooltip = "Click me!"

        m = folium.Marker(
            self.coords,
            popup=folium.Popup(htmlcode, min_width=300, max_width=300),
            icon=folium.Icon(color='black', icon_color=person_colour)
            # tooltip=tooltip,
        )
        return(m)


# For Harmony table, get column number
# for a given question number
def get_question_column(q):
    return(3 + 4*(q-1))


# For a given location string,
# return the final coords from locations.tsv
def query_location(loc):
    l = locations.loc[locations['loc_string'] == loc].iloc[:, 3:]
    return l.values.flatten().tolist()


# Iterate over harmony data row by row,
# storing Answer class objects to answers
answers = []

for i in range(harmony_data.index.stop):
    x = harmony_data.loc[i, :].values.flatten().tolist()
    name = x[0]
    questions = sorted(x[2].split(','))

    # Use question number to select columns
    for question in questions:
        q_num = int(question[1])
        assert q_num in range(1, 10)
        q_col = get_question_column(q_num)
        loc = x[q_col].strip()
        coords = query_location(loc)
        assert coords
        text = x[q_col+1]
        img = x[q_col+2]

        # Retrieve images if not nan and not already downloaded
        if str(img) == 'nan':
            img_name = ''
            img_link = ''
        else:
            img_name = ''.join([name, '_', str(q_num), '.jpeg'])
            img_link = img[img.find("(")+1:img.find(")")]
            if exists(''.join(['img/', img_name])):
                pass
            else:
                urllib.request.urlretrieve(img_link, ''.join(['img/', img_name]))

        answers.append(Answer(name, loc, coords, question, text, img_name, img_link))


# Add answers to question groups
for answer in answers:
    for group in groups:
        if answer.question == group.layer_name:
            group.add_child(answer.marker())


# Add category toggle menu
folium.LayerControl(collapsed=False).add_to(m)


# Output to file
m.save("map.html")
