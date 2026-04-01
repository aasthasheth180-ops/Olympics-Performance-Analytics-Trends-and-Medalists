import streamlit as st
import pandas as pd
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

# 1. Load datasets
athletes_df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

# 2. Preprocess
df = preprocessor.preprocess(athletes_df, region_df)

# 3. Sidebar - Season Selection
st.sidebar.title("Olympics Analysis")
season = st.sidebar.selectbox('Select Season', ('Summer', 'Winter'))

# 4. Filter by Season
df_season = df[df['Season'] == season]

# 5. Sidebar - Analysis Options
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete wise Analysis')
)

if user_menu == 'Medal Tally':
    st.sidebar.header(f"{season} Olympics Medal Tally")
    years, country = helper.country_year_list(df_season)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    tally = helper.fetch_medal_tally(df_season, selected_year, selected_country)

    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title('Overall Tally')
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country} Overall Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"{selected_year} Overall Tally")
    else:
        st.title(f"{selected_year} Performance In {selected_country}")

    st.dataframe(tally)

elif user_menu == 'Overall Analysis':
    Editions = df_season['Year'].unique().shape[0] - 1
    Cities = df_season['City'].unique().shape[0]
    Sports = df_season['Sport'].unique().shape[0]
    Events = df_season['Event'].unique().shape[0]
    Athletes = df_season['Name'].unique().shape[0]
    Nations = df_season['region'].unique().shape[0]

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(Editions)
    with col2:
        st.header("Cities")
        st.title(Cities)
    with col3:
        st.header("Sports")
        st.title(Sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(Events)
    with col2:
        st.header("Athletes")
        st.title(Athletes)
    with col3:
        st.header("Nations")
        st.title(Nations)

    nations_over_time = helper.data_over_time(df_season, 'region')
    fig1 = px.line(nations_over_time, x='Editions', y='region')
    st.title("Participating Nations Over The Year")
    st.plotly_chart(fig1)

    events_over_time = helper.data_over_time(df_season, 'Event')
    fig2 = px.line(events_over_time, x='Editions', y='Event')
    st.title("Events Played Over The Year")
    st.plotly_chart(fig2)

    st.title("No. of Events over time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x_pivot = df_season.drop_duplicates(['Year', 'Sport', 'Event'])
    pivot = x_pivot.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int')
    ax = sns.heatmap(pivot, annot=True)
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sport_list = df_season['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    selected_sport = st.selectbox("Select a Sport", sport_list)
    x_athletes = helper.most_successful(df_season, selected_sport)
    st.table(x_athletes)

elif user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')
    years, countries = helper.country_year_list(df_season)
    if 'Overall' in countries:
        countries.remove('Overall')

    selected_country = st.sidebar.selectbox('Select a Country', countries, key='country_analysis_box')
    country_df = helper.yearwise_medal_tally(df_season, selected_country)
    
    if country_df.empty:
        st.warning(f"No medals recorded for {selected_country}.")
    else:
        fig = px.line(country_df, x='Year', y='Medal')
        st.title(f"{selected_country} Medal Tally Over the Year")
        st.plotly_chart(fig)

    st.title(f"{selected_country} Excels In The Following Event")
    pt = helper.country_event_heatmap(df_season, selected_country)
    if pt.empty:
        st.write("No sport-specific data available.")
    else:
        fig, ax = plt.subplots(figsize=(20, 20))
        ax = sns.heatmap(pt, annot=True)
        st.pyplot(fig)

    st.title(f"Top 10 athletes of {selected_country}")
    top10_df = helper.most_successful_countrywise(df_season, selected_country)
    st.table(top10_df)

elif user_menu == 'Athlete wise Analysis':
    st.sidebar.title('Athlete-wise Analysis')

    # 1. Age Distribution
    athlete_df = df_season.drop_duplicates(subset=['Name', 'region'])
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'], show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution Of Age")
    st.plotly_chart(fig, key='age_dist_overall')

    # 2. Distribution of Age wrt Sports (Gold Medalists)
    st.title("Distribution Of Age wrt Sports (Gold Medalist)")
    famous_sports = ['Basketball', 'Judo', 'Football', 'Athletics', 'Swimming', 'Gymnastics', 'Wrestling', 'Hockey', 'Rowing', 'Fencing', 'Shooting', 'Boxing', 'Cycling']
    
    x_dist = []
    name_dist = []
    for sport in famous_sports:
        temp_df = df_season[df_season['Sport'] == sport]
        gold_ages = temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna()
        if len(gold_ages) > 2: 
            x_dist.append(gold_ages)
            name_dist.append(sport)

    if x_dist:
        fig2 = ff.create_distplot(x_dist, name_dist, show_hist=False, show_rug=False)
        fig2.update_layout(autosize=False, width=1000, height=600)
        st.plotly_chart(fig2, key='age_dist_sports')
    
    # 3. Height vs Weight Scatter Plot
    st.title('Height vs Weight')
    sport_list = df_season['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    selected_sport = st.selectbox("Select a Sport", sport_list, key='h_vs_w_sport')
    temp_df = helper.weight_vs_height(df_season, selected_sport)
    
    # CRITICAL: Drop missing values so plot isn't blank
    temp_df = temp_df.dropna(subset=['Height', 'Weight'])

    if temp_df.empty:
        st.warning(f"No height/weight data available for {selected_sport}.")
    else:
        temp_df = temp_df.sort_values('Medal', ascending=False)
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.scatterplot(data=temp_df, x='Weight', y='Height', hue='Medal', style='Sex', s=80, alpha=0.7, ax=ax)
        st.pyplot(fig)
    
    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df_season)
    fig3 = px.line(final,x='Year',y=['Male','Female'])
    fig3.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig3)
    plt.clf()

else:
    st.dataframe(df_season)