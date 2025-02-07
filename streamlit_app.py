import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV data
data = pd.read_csv('Blast.csv')
mlb_data = pd.read_csv('MLB_Blast.csv')

# Function to calculate Swing Score
def calc_swing_score(swing_acceleration, min_swing_acc=15, max_swing_acc=30):
    score = 20 + ((swing_acceleration - min_swing_acc) / (max_swing_acc - min_swing_acc)) * 60
    return max(min(score, 80), 20)  # Ensure score is within the 20-80 range

# Function to calculate Euclidean distance
def euclidean_distance(x1, y1, z1, x2, y2, z2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

# Function to assign color category based on input values and cluster centroids
def assign_color_category(bat_speed, swing_acceleration, attack_angle):
    clusters = {
        "Orange": [73.3, 24.03, 8.84],
        "Purple": [71.2, 24.66, 8.41],
        "Red": [69.9, 22.21, 10.39],
        "Grey": [69.3, 22.21, 14.47],
        "Green": [65.9, 22.29, 8.47],
        "Pink": [68.7, 20.48, 10.34],
        "Brown": [68.9, 22.47, 6.33],
        "Blue": [64.4, 20.4, 8.99]
    }

    distances = {color: euclidean_distance(bat_speed, swing_acceleration, attack_angle, *coords)
                 for color, coords in clusters.items()}
    return min(distances, key=distances.get)

# Define descriptions and expected metrics for each category
category_info = {
    "Orange": {
        "description": 
                       "Very efficient to the ball and finds success in utilizing the high bat speed to hit pitches out in front for power. This group may be plagued by a high whiff rate.",
        "metrics": "wOBA: .323, Whiff Pct: 25.9, Barrel Pct: 11.51, Batting Avg: .245, ISO: .185"
    },
    "Purple": {
        "description": 
                       "This group is the most efficient to the ball and is full of complete hitters that can hit for average and power. Hitters in this group who struggle likely are finding their efficiency by hitting balls too deep.",
        "metrics": "wOBA: .318, Whiff Pct: 23.22, Barrel Pct: 9.37, Batting Avg: .245, ISO: .168"
    },
    "Red": {
        "description": 
                       "This cluster consists of slightly longer than average swings that take longer than average from start to impact, but generally benefit from hitting the ball in front of the plate. These longer swings may result in too many whiffs.",
        "metrics": "wOBA: .312, Whiff Pct: 24.65, Barrel Pct: 9.22, Batting Avg: .241, ISO: .172"
    },
    "Grey": {
        "description": 
                       "Relatively normal swings in the context of bat speed and swing length, but follow a very uppercut path. These swings find production through power, while hitting for a low average and whiffing often.",
        "metrics": "wOBA: .300, Whiff Pct: 28.06, Barrel Pct: 10.16, Batting Avg: .216, ISO: .171"
    },
    "Green": {
        "description": 
                       "This group consists of slow to average bat speeds but all very efficient swings. They find success in strong utilization of bat to ball skills and may struggle with too steep of an attack angle.",
        "metrics": "wOBA: .298, Whiff Pct: 18.45, Barrel Pct: 4.81, Batting Avg: .242, ISO: .111"
    },
    "Pink": {
        "description": 
                       "This group has high variance with its best hitters finding success by elevating the ball to the pull side, thanks to a point of contact well in front of the plate. The hitters who struggle in this group are due to their high swing length being a product of a truly long swing, not a point of contact that results in pulled fly balls.",
        "metrics": "wOBA: .293, Whiff Pct: 24.27, Barrel Pct: 7.92, Batting Avg: .221, ISO: .150"
    },
    "Brown": {
        "description": 
                       "Slightly slower swings with a very flat attack angle. If these swings are successful it’s likely because of a strong contact-oriented approach. They don’t whiff much but may struggle to hit for power.",
        "metrics": "wOBA: .284, Whiff Pct: 20.49, Barrel Pct: 5.10, Batting Avg: .235, ISO: .113"
    },
    "Blue": {
        "description":
                       "This group generally struggles, with a low bat speed and not getting to that bat speed quickly. The hitters who find success are doing so through a contact-oriented approach with the margin for error being razor thin.",
        "metrics": "wOBA: .273, Whiff Pct: 19.75, Barrel Pct: 3.43, Batting Avg: .222, ISO: .093"
    }
}

def calculate_launch_angle(attack_angle, approach_angle=-6):
    launch_angle = attack_angle - approach_angle
    return launch_angle

def find_closest_swings(bat_speed, swing_length, swing_acceleration, n=5):
    distances = mlb_data.apply(
        lambda row: euclidean_distance(bat_speed, swing_length, swing_acceleration, row['Bat Speed'], row['Swing Length'], row['Swing Acceleration']),
        axis=1
    )
    closest_indices = distances.nsmallest(n).index
    return mlb_data.iloc[closest_indices]

def flip_name(name):
    last, first = name.split(', ')
    return f"{first} {last}"

# Streamlit app code
st.set_page_config(
    page_title='Swing Metrics Calculator',
    page_icon="https://static.wixstatic.com/media/7383ad_9fe67936506547e19ad5985ef14c8142~mv2.png/v1/fill/w_400,h_400,al_c,q_85,usm_1.20_1.00_0.01,enc_avif,quality_auto/CBH%20Logo.png",
)

# Add custom CSS for background image
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://img.freepik.com/free-photo/light-background_24972-1415.jpg");
        background-size: cover; /* Adjust background size */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Swing Metrics and Trajectory Calculator')

# Select name from data
selected_name = st.selectbox('Select Player', data['Name'])

# Get selected player data
player_data = data[data['Name'] == selected_name].iloc[0]
bat_speed = player_data['Bat Speed (mph)']
attack_angle = player_data['Attack Angle (deg)']
time_to_contact = player_data['Time to Contact (sec)']
swing_length = player_data['Swing Length']
swing_acceleration = player_data['Swing Acceleration']

# Calculate swing score, color category, and launch angle
swing_score = calc_swing_score(swing_acceleration)
color_category = assign_color_category(bat_speed, swing_acceleration, attack_angle)
launch_angle = calculate_launch_angle(attack_angle)

# Find closest MLB swings
closest_swings = find_closest_swings(bat_speed, swing_length, swing_acceleration)
closest_names = [flip_name(name) for name in closest_swings['Name']]

# Determine color based on swing score
if swing_score >= 60:
    score_color = '#4CAF50'  # Green
elif swing_score >= 40:
    score_color = '#FFA500'  # Orange
else:
    score_color = '#FF0000'  # Red

# Display the results in columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Bat Speed", f"{bat_speed:.2f} mph")
col2.metric("Swing Length", f"{swing_length:.2f} feet")
col3.metric("Swing Acceleration", f"{swing_acceleration:.2f} g")
col4.metric("Attack Angle", f"{attack_angle:.2f} deg")

# Display the swing score as a donut chart with the score in the center
st.subheader('Swing Score Visualization')
fig, ax = plt.subplots()
fig.patch.set_alpha(0)  # Make the background transparent
ax.pie([swing_score - 20, 80 - swing_score], labels=['', ''], colors=[score_color, '#E0E0E0'], startangle=90, counterclock=False, wedgeprops=dict(width=0.3))
ax.text(0, 0, f"{swing_score:.2f}", ha='center', va='center', fontsize=24, weight='bold', color='#FFFFFF')  # Change text color to white
ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
st.pyplot(fig)

# Display the color category and category information
st.subheader(f"Color Category: {color_category}")
st.markdown(f"<h3>Description:</h3> <p style='font-size:20px;'>{category_info[color_category]['description']}</p>", unsafe_allow_html=True)
st.write(f"**Metrics:** {category_info[color_category]['metrics']}")

# Display the closest MLB swings
st.subheader("Closest MLB Swings")
for name in closest_names:
    st.write(name)

