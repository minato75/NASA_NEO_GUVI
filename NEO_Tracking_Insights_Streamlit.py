import streamlit as st
import pymysql
import pandas as pd
from datetime import date

# Function to connect to the MySQL database
import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
        user="m5Xt4HUDrniTj1o.root",
        password="JhWWCZgwpY56epBA",
        database="NEO",          
        ssl_verify_cert=False,                  # Optional: disable if cert verification fails
        ssl_disabled=False                      # TiDB requires SSL
    )
    return connection

    

queries = {
    "1.Count how many times each asteroid has approached Earth":
            """select neo_reference_id as AsteroidID ,count(*) as HowManyTimesApproached from close_approach group by neo_reference_id order by HowManyTimesApproached desc""",

    "2.Average velocity of each asteroid over multiple approaches":
        """elect neo_reference_id as AsteroidID,avg(relative_velocity_kmph) as AverageVelocityKmph from close_approach group by AsteroidID having count(AsteroidID)>1 order by AverageVelocityKmph desc""",

    "3.List top 10 fastest asteroids":
        """select neo_reference_id as AsteroidID,relative_velocity_kmph as Velocity_Kmph from close_approach order by Velocity_Kmph desc limit 10""",

    "4.Find potentially hazardous asteroids that have approached Earth more than 3 times":
        """select asteroids.id as AsteroidID,count(close_approach.neo_reference_id) as ApproachCount from asteroids  join close_approach  on asteroids.id = close_approach.neo_reference_id where asteroids.is_potentially_hazardous_asteroid = TRUE group by asteroids.id having count(*)>3 order by ApproachCount desc""",

    "5.Find the month with the most asteroid approaches":
        """select date_format(close_approach_date,'%Y-%m') as Month,count(*) as count from close_approach group by Month order by count Desc limit 1""",

    "6.Get the asteroid with the fastest ever approach speed":
        """select asteroids.name,max(close_approach.relative_velocity_kmph) as SpeedinKmpH from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id group by asteroids.name order by SpeedinKmpH desc""",

    "7.Sort asteroids by maximum estimated diameter (descending)":
       """select name,estimated_diameter_max_km from asteroids group by name,estimated_diameter_max_km order by estimated_diameter_max_km desc""",

    "8.Asteroids whose closest approach is getting nearer over time":
        """select asteroids.name,close_approach.miss_distance_km,close_approach.close_approach_date from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id order by close_approach.miss_distance_km, close_approach.close_approach_date desc limit 1""",

    "9.Display name of each asteroid with date and miss distance of its closest approach":
        """select asteroids.name,close_approach.miss_distance_km,close_approach.close_approach_date from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id order by close_approach.miss_distance_km, close_approach.close_approach_date desc""",

    "10.List names of asteroids with velocity > 50,000 km/h":
        """ select asteroids.name from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id where (close_approach.relative_velocity_kmph > 50000) order by asteroids.name  desc """,

    "11.Count how many approaches happened per month":
        """select date_format(close_approach.close_approach_date,'%Y-%m') as Month,count(*) as count from close_approach group by Month order by Month asc""",

    "12.Find asteroid with the highest brightness (lowest magnitude value)":
        """select name,id,absolute_magnitude_h from asteroids where absolute_magnitude_h=(select min(absolute_magnitude_h) from asteroids) """,

    "13.Get number of hazardous vs non-hazardous asteroids":
       """ select sum(is_potentially_hazardous_asteroid=true)as Hazard,sum(is_potentially_hazardous_asteroid=false) as NonHazard from asteroids """,

    "14.Asteroids that passed closer than the Moon (miss_dist < 1 LD)":
       """select asteroids.nameas Name_of_Asteroid,close_approach.miss_distance_lunar,close_approach.close_approach_date from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id where (close_approach.miss_distance_lunar < 1) order by close_approach.miss_distance_lunar desc""",

    "15.Asteroids that came within 0.05 AU":
        """ select asteroids.name as Name_of_Asteroid,close_approach.astronomical from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id where (close_approach.astronomical < 0.05) order by close_approach.astronomical desc""",
    "16.Average estimated diameter of all asteroids":
         """select avg(estimated_diameter_max_km) from asteroids""",
    "17.Find the asteroid with the most recorded approaches":
        """sselect asteroids.name as Name_of_Asteroid,count(close_approach.neo_reference_id) as No_of_times_approached from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id group by asteroids.name order by count(close_approach.neo_reference_id) desc limit 1""",
    "18.Find asteroids that have approached Earth more than 1 year":
        """select asteroids.name as Name_of_Asteroid,count(distinct year(close_approach.close_approach_date)) as No_of_Years_approached from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id group by asteroids.name having count(distinct year(close_approach.close_approach_date))>1 order by No_of_Years_approached desc""",
    "19.Total number of asteroid approaches each year":
        """select year(close_approach_date) as Year, count(*) as No_of_approches from close_approach group by year(close_approach_date) order by year(close_approach_date) asc""",
    "20.Find asteroids that have only approached Earth once":
        """select asteroids.name as Name_of_Asteroid from asteroids join close_approach on asteroids.id = close_approach.neo_reference_id group by asteroids.name having count(distinct (close_approach.neo_reference_id))=1 """}

st.set_page_config(page_title="Asteroid Insights", layout="wide")  
# Set up Streamlit

st.title(" NASA Asteroid Tracker 🪐")

# Query toggle
if "query" not in st.session_state:
    st.session_state.query = False

st.sidebar.markdown("---")
st.sidebar.markdown("### Query")
if st.sidebar.button("Queries"):
    st.session_state.query = not st.session_state.query

# Query Selection and Execution
if st.session_state.query:
    selected_query = st.selectbox("Choose a query to run:", list(queries.keys()))

    try:
        conn = get_connection()
        cur_sor = conn.cursor()
        cur_sor.execute(queries[selected_query])
        results = cur_sor.fetchall()
        df = pd.DataFrame(results)

        st.subheader("📊 Query Result")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# Filter toggle
if "show_filters" not in st.session_state:
    st.session_state.show_filters = False

st.sidebar.markdown("---")
st.sidebar.markdown("### Apply Custom Filters")
if st.sidebar.button("Filter Criteria"):
    st.session_state.show_filters = not st.session_state.show_filters

# Filter UI
if st.session_state.show_filters:
    st.subheader("🔍 Filter Criteria")

    col1, col2, col3 = st.columns(3)

    with col1:
        magnitude_range = st.slider("Magnitude Range", 10.4, 32.38, (10.4, 32.38))
        min_diameter = st.slider("Min Estimated Diameter (km)", 0.0008882904, 22.10828, (0.0008882904, 22.10828))
        max_diameter = st.slider("Max Estimated Diameter (km)", 0.0019862778,49.43562, (0.0019862778,49.43562))

    with col2:
        velocity_range = st.slider("Relative Velocity (km/h)", 1054.2612, 186135.89, (1054.2612, 186135.89))
        au_range = st.slider("Astronomical Unit", 0.0004684885,0.49989605, (0.0004684885,0.49989605))
        hazardous_only = st.selectbox("Only Show Potentially Hazardous", [0, 1])

    with col3:
        start_date = st.date_input("Start Date", value=date(2025, 5, 1))
        end_date = st.date_input("End Date", value=date(2027,7,29))

    if st.button("Apply Filter"):
        try:
            conn = get_connection()
            cur_sor = conn.cursor()

            # Get all filter values
            mag_min, mag_max = magnitude_range
            dia_min_min, dia_min_max = min_diameter
            dia_max_min, dia_max_max = max_diameter
            vel_min, vel_max = velocity_range
            au_min, au_max = au_range
            haz = hazardous_only
            start = start_date.strftime('%Y-%m-%d')
            end = end_date.strftime('%Y-%m-%d')
            # Build SQL query dynamically
            filter_query = f"""
            select a.name, a.absolute_magnitude_h, a.estimated_diameter_min_km, a.estimated_diameter_max_km,
            a.is_potentially_hazardous_asteroid, ca.close_approach_date, ca.relative_velocity_kmph,
            ca.astronomical, ca.miss_distance_km
            from asteroids a
            join close_approach ca on a.id = ca.neo_reference_id
            where a.absolute_magnitude_h between {mag_min} and {mag_max}
            and a.estimated_diameter_min_km between {dia_min_min} and {dia_min_max}
            and a.estimated_diameter_max_km between {dia_max_min} and {dia_max_max}
            and ca.relative_velocity_kmph BETWEEN {vel_min} and {vel_max}
            and ca.astronomical BETWEEN {au_min} and {au_max}
            and a.is_potentially_hazardous_asteroid = {haz}
            and ca.close_approach_date BETWEEN '{start}' and '{end}'
            order by ca.close_approach_date asc
            """

            cur_sor.execute(filter_query)
            results = cur_sor.fetchall()
            df = pd.DataFrame(results)

            if df.empty:
                st.warning("No data found for the applied filters.")
            else:
                st.success("Filtered data displayed below:")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error running filter: {e}")   
        finally:
            if 'conn' in locals():
                conn.close()     