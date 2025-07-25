"""creates streamlit dashboard"""
import awswrangler as wr
import pandas as pd
import altair as alt
import streamlit as st
import pymssql
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta


def create_title(title_str: str) -> None:
    """Creates the title"""
    st.title(title_str)


@st.cache_data
def load_from_athena() -> pd.DataFrame:
    """Loads all data from the Athena"""
    return wr.athena.read_sql_query("SELECT plant_id, mean_soil_moisture, mean_soil_temperature, date, watering_count,"
                                    "most_recent, english_name, country_name FROM summary INNER JOIN plant"
                                    " ON summary.plant_id = plant.id"
                                    " INNER JOIN origin ON plant.origin_id = origin.id"
                                    " INNER JOIN city on origin.city_id= city.id"
                                    " INNER JOIN country on city.country_id=country.id;", database="c18_botanists_db")


def get_connection():
    """get rds connection"""
    load_dotenv()
    conn = pymssql.connect(
        os.environ["DB_HOST"],
        os.environ["DB_USER"],
        os.environ["DB_PASSWORD"],
        os.environ["DB_NAME"]
    )
    return conn


@st.cache_data(ttl=120)
def load_from_rds() -> pd.DataFrame:
    """load data from rds"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT reading.id, reading.reading_taken, reading.last_watered,
            reading.soil_moisture, reading.soil_temperature, reading.plant_id,
            reading.botanist_id, plant.english_name, plant.scientific_name,
            botanist.botanist_name, botanist.botanist_email
            FROM reading JOIN plant on reading.plant_id = plant.id LEFT JOIN botanist
            ON reading.botanist_id = botanist.id"""
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()
        conn.close()
    return df


def live_temp_moisture():
    """line graph for temp/moisture over time"""
    st.write("### Plants moisture/temp over time")
    df = load_from_rds()

    df['id_name'] = df['plant_id'].astype(str) + '-' + df['english_name']

    df['last_watered'] = pd.to_datetime(df['last_watered'], errors='coerce')
    df['reading_taken'] = pd.to_datetime(df['reading_taken'], errors='coerce')

    plant_ids = df['id_name'].unique()
    plant = st.sidebar.selectbox('Select plant', plant_ids)
    selected = int(plant.split('-')[0])

    metric = st.radio('Temp or Moisture', [
                      'soil_moisture', 'soil_temperature'])

    filtered = df[df['plant_id'] == selected]
    filtered = filtered.sort_values('reading_taken')

    filtered[metric] = pd.to_numeric(filtered[metric], errors='coerce')

    filtered['diff'] = filtered[metric].diff()

    filtered = filtered[filtered['diff'].isna() | (
        filtered['diff'].abs() < 10)]
    earliest_reading = filtered['reading_taken'].min()

    watered_series = (
        df[(df['plant_id'] == selected) & (df['last_watered'] > earliest_reading)]
        ['last_watered']
        .drop_duplicates()
        .dropna()
        .reset_index(drop=True)
    )

    watered_events = pd.DataFrame({'last_watered': watered_series})

    chart = alt.Chart(filtered).mark_line().encode(
        x='reading_taken:T',
        y=f"{metric}:Q",
    ).properties(width=700, height=400)

    watered = alt.Chart(watered_events).mark_rule(color='red', size=2).encode(
        x='last_watered:T'
    )
    final = chart + watered

    st.altair_chart(final)


def dry_plant():
    """finds sub 40% moisture plants"""
    st.write("### Plants with sub 40% moisture")
    df = load_from_rds()
    latest = df.sort_values('reading_taken').groupby(
        'plant_id', as_index=False).last()
    dry = latest[latest['soil_moisture'] < 40]
    botanists = dry['botanist_name'].dropna().unique()
    selected_botanist = st.selectbox(
        'select botanist', ['All']+list(botanists))
    if selected_botanist != 'All':
        dry = dry[dry['botanist_name'] == selected_botanist]

    st.dataframe(
        dry[['english_name', 'plant_id', 'reading_taken', 'botanist_name', 'soil_moisture', 'last_watered']])


def filter_unwatered_plants():
    """Finds unwatered plants"""
    df = load_from_rds()
    st.write("### Plants Not Watered in the Last 24 Hours")
    df['last_watered'] = pd.to_datetime(df['last_watered'], errors='coerce')

    latest_watered = df.sort_values('last_watered').groupby(
        'plant_id', as_index=False).last()

    cutoff = datetime.now() - timedelta(days=1)
    overdue = latest_watered[latest_watered['last_watered'] < cutoff]
    botanists = overdue['botanist_name'].dropna().unique()
    selected_botanist = st.selectbox(
        'select botanist:', ['All']+list(botanists))
    if selected_botanist != 'All':
        overdue = overdue[overdue['botanist_name'] == selected_botanist]

    st.dataframe(
        overdue[['english_name', 'plant_id', 'last_watered', 'botanist_name', 'botanist_email']])


def summary_country_data():
    """finds summary data by country"""
    df = load_from_athena()
    st.write("### temp/moisture by country")
    metric = st.radio('Temp or Moisture', [
                      'mean_soil_moisture', 'mean_soil_temperature'])
    mean_val = df.groupby('country_name')[metric].mean().reset_index()
    chart = alt.Chart(mean_val).mark_bar().encode(
        x=alt.X('country_name:N', sort='-y', title='country of origin'),
        y=alt.Y(f"{metric}:Q")
    ).properties(width=600, height=400)
    st.altair_chart(chart)


def summary_watering():
    """finds which plants get watered the most"""
    df = load_from_athena()
    st.write("### plants that are most watered")
    df['plant_label'] = df['plant_id'].astype(str) + '-' + df['english_name']
    mean_water_count = df.groupby('plant_label')[
        'watering_count'].mean().reset_index()
    chart = alt.Chart(mean_water_count).mark_bar().encode(
        x=alt.X('plant_label:N', sort='-y', title='country of origin'),
        y=alt.Y("watering_count:Q", title='mean number of watering times a day')
    ).properties(width=600, height=400)
    st.altair_chart(chart)


def temp_moisture_scatter():
    """scatter plot of temp vs moisture"""
    st.write("### Temperature vs moisture scatter plot")

    df = load_from_athena()
    df["date"] = pd.to_datetime(df["date"])
    # Scatter plot: Temperature vs Moisture
    chart = alt.Chart(df).mark_circle(size=80).encode(
        x=alt.X("mean_soil_temperature:Q", title="Mean Temperature"),
        y=alt.Y("mean_soil_moisture:Q", title="Mean Moisture"),
        tooltip=[
            alt.Tooltip("plant_id:N", title="Plant ID"),
            alt.Tooltip("english_name:N", title="Plant Name"),
            alt.Tooltip("date:T", title="Date")
        ],
        color=alt.Color("english_name:N", legend=None)
    ).properties(
        width=700,
        height=450
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def daily_page():
    """create daily page"""
    create_title("Daily data")
    st.write('Data for plants so far today')
    live_temp_moisture()
    dry_plant()
    filter_unwatered_plants()


def summary_page():
    """create summary page"""
    create_title("Summary data")
    st.write("Historical data")
    summary_country_data()
    summary_watering()
    temp_moisture_scatter()


def home():
    """home page"""
    page = st.selectbox("choose a page", ['daily', 'summary'])
    if page == 'daily':
        daily_page()
    if page == 'summary':
        summary_page()


if __name__ == "__main__":
    home()
