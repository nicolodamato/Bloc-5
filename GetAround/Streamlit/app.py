import base64
import pandas as pd
pd.options.mode.chained_assignment = None
import requests
import streamlit as st
import streamlit.components.v1 as components
import joblib
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="GetAround Analysis",
    page_icon="🚗",
)

# IMPORT DATASET
@st.cache(allow_output_mutation=True)
def delay():
  df_delay = pd.read_excel("get_around_delay_analysis.xlsx")
  return df_delay

df_delay = delay()

# outliers removed
df_no_outliers = df_delay[(df_delay.delay_at_checkout_in_minutes > -720) & (df_delay.delay_at_checkout_in_minutes < 720)]
# create a new dataset without missing values on previous ended rental id
df1 = df_delay
# create a second dataset without missing values in previous ended rental id
df2 = df_delay[df_delay["previous_ended_rental_id"].isna() == False]
# create a new column delay in both datasets
df1['delay'] = df1['delay_at_checkout_in_minutes'].apply(lambda x: 'delayed' if x > 0 else 'in time')
df2['delay'] = df2['delay_at_checkout_in_minutes'].apply(lambda x: 'delayed' if x > 0 else 'in time')
# add 1st_rental and 2nd_rental in datasets column to separate rentals 
df1 = df1.add_prefix('1st_rental_')
df2 = df2.add_prefix('2nd_rental_')
# make corrections
df1.rename(columns={'1st_rental_rental_id': '1st_rental_id'}, inplace=True)
df2.rename(columns={'2nd_rental_rental_id': '2nd_rental_id'}, inplace=True)
# create a new column to make the join possible
df1['join'] = df1['1st_rental_id']
df2['join'] = df2['2nd_rental_previous_ended_rental_id'].apply(lambda x: int(x))
# join datasets
df = df1.merge(df2, on='join')
# drop useless columns
df = df.drop(['join', "1st_rental_state", '2nd_rental_car_id', '1st_rental_previous_ended_rental_id', '1st_rental_time_delta_with_previous_rental_in_minutes' , '2nd_rental_id', '2nd_rental_delay_at_checkout_in_minutes','1st_rental_previous_ended_rental_id'], axis=1)
# create a new dataset containig only 2nd rentals canceled states
df_canceled = df[df['2nd_rental_state'] == "canceled"]
# keep only delayed canceled states
df_canceled_late = df_canceled[df_canceled['1st_rental_delay_at_checkout_in_minutes'] > 0]
# this ratio let us calculate the proportion beetween 1st rental delay & the time delta among the two rentals
ratio = df_canceled_late['1st_rental_delay_at_checkout_in_minutes'].sum() / df_canceled_late['2nd_rental_time_delta_with_previous_rental_in_minutes'].sum() 
# average time delta 
mean = round(df_canceled_late['2nd_rental_time_delta_with_previous_rental_in_minutes'].mean(), 0)
# minimum threshold in minutes
res = round(ratio * mean, 0)
# let's see the number of rentals with a time delta Under or Over the threshold
df_canceled_late['state_within_threshold'] = df_canceled_late['1st_rental_delay_at_checkout_in_minutes'].apply(lambda x: 'in time' if x < 130 else 'delayed')
# create a new column with 1st rentals delays if the threshold was been etablished
df['1st_rental_delay_within_threshold'] = df['1st_rental_delay_at_checkout_in_minutes'].apply(lambda x: 'in time' if x < 130 else 'delayed')
# create a new column with 2nd rentals states if the threshold was been etablished
df['2nd_rental_state_within_threshold'] = df['1st_rental_delay_at_checkout_in_minutes'].apply(lambda x: 'ended' if x < 130 else 'canceled')

st.title('GetAround Analysis 🚗')

fig = px.histogram(df_delay, x="state",
                   title = 'Proportion of rental states (canceled / ended)',
                      histnorm= 'percent',
                      barmode ='group',
                      width= 800,
                      height = 500,
                      text_auto = True,
                      color_discrete_sequence=px.colors.sequential.Blues_r)                    
fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = '',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )
st.plotly_chart(fig)

st.markdown('- __Only 15 % of rentals has been canceled.__')

# create a dictionnary to showing checkin-type values
values = dict(df_delay.checkin_type.groupby(df_delay.checkin_type).count())

fig = px.pie(values.items(), values= values.values(), names= values.keys(), color= values,
             title = 'Proportion of checkin types ',                                                          
            color_discrete_sequence=px.colors.sequential.Blues_r)
fig.update_traces(textposition = 'outside', textfont_size = 15)             
fig.update_layout(title_x = 0.5, 
                    margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                    template = 'plotly_dark'
                    )
st.plotly_chart(fig)

st.markdown('- __We can observe that only 20 % of users utilize the connect checkin.__')
st.markdown('- __Users still prefer the connect type (80 %).__')

fig = px.histogram(df_no_outliers, x="delay_at_checkout_in_minutes",
                      color = 'checkin_type',
                      title = 'Rentals distribution for a delay at checkout in minutes within 12 hours range',
                      barmode ='group',
                      width= 800,
                      height = 600,
                      color_discrete_map={'connect':'lightcyan',
                                          'mobile':'royalblue',
                                })
                    
fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = '',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )
st.plotly_chart(fig)

st.markdown('- __The majority of the delay within checkout distribution is between -200 and 200 minutes.__')

fig = px.histogram(df, x="2nd_rental_delay",
                      color = '1st_rental_delay',
                      title = 'Proportion of 2nd rental delayed & in time cars depending on 1st rental delay',
                      histnorm= 'percent',
                      barmode ='group',
                      width= 800,
                      height = 600,
                      text_auto = True,
                      color_discrete_sequence=px.colors.sequential.Blues_r)
st.plotly_chart(fig)

st.markdown('__About the second rentals delay depending on the first rental one, we can observe that :__')
st.markdown('- If the __first rent is delayed__, 52 % of second rentals will be on time and 48 % will delay.')
st.markdown('- If the __first rent is on time__, 60 % of second rentals will be on time and 40 % will delay.')

st.header('Threshold: how long should the minimum delay be?')
st.subheader(f'After some analysis on canceled rentals, we observed that tht the minimum delay should be {res} min.')

# show the relation between in time and delayed rentals in canceled rentals if the threshold was been etablished
state_within_threshold = dict(df_canceled_late.state_within_threshold.groupby(df_canceled_late.state_within_threshold).count())

fig = px.pie(state_within_threshold.items(), values= state_within_threshold.values(), 
              title = 'Percentage of rentals states in canceled rentals if the threshold was been established', 
              names= state_within_threshold.keys(), color= state_within_threshold,
             color_discrete_sequence=px.colors.sequential.Blues_r)
fig.update_traces(textposition = 'outside', textfont_size = 15)             
fig.update_layout(title_x = 0.5, 
                    margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                    template = 'plotly_dark'
                    )  
st.plotly_chart(fig)

st.markdown('- __We notice that if the threshold was been in place, only 28 % of canceled rentals would have been dalayed.__')

col1, col2 = st.columns(2)

with col1:

    fig = px.histogram(df, x="1st_rental_delay_within_threshold",
                      title = 'Proportion of 1st rental delays WITH threshold',
                      histnorm= 'percent',
                      barmode ='group',
                      width= 400,
                      height = 400,
                      text_auto = True,
                      color_discrete_sequence=px.colors.sequential.Blues_r)
                    
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = '',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )  

    st.plotly_chart(fig)

with col2:

    fig = px.histogram(df, x="1st_rental_delay",
                      title = 'Proportion of 1st rental delays WITHOUT threshold',
                      histnorm= 'percent',
                      barmode ='group',
                      width= 400,
                      height = 400,
                      text_auto = True,
                      color_discrete_sequence=px.colors.sequential.Blues)
                    
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = '',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )  

    st.plotly_chart(fig)

st.markdown("- __WITH the threshold in place, only 14 % of rentals would have been delayed.__")
st.markdown("- __WITHOUT the threshold, almost 1 rental in two was delayed.__")


st.subheader("Rentals states WITH/WITHOUT threshold")
col1, col2 = st.columns(2)

with col1 :
  # show the final state in 2nd rentals with threshold
  final_state_within_threshold = dict(df['2nd_rental_state_within_threshold'].groupby(df['2nd_rental_state_within_threshold']).count())

  fig = px.pie(final_state_within_threshold.items(), values= final_state_within_threshold.values(), names= final_state_within_threshold.keys(), color= final_state_within_threshold,
              width= 400,
              height = 400,                                                                                                                              
              title=  "WITH threshold",
              color_discrete_sequence=px.colors.sequential.Blues_r)
  fig.update_traces(textposition = 'outside', textfont_size = 15)             
  fig.update_layout(title_x = 0.5, 
                    margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                    template = 'plotly_dark'
                    )  

  st.plotly_chart(fig)
   

with col2 :
  # show rentals states without threshold
  state_without_threshold = dict(df['2nd_rental_state'].groupby(df['2nd_rental_state']).count())

  fig = px.pie(state_without_threshold.items(), values= state_without_threshold.values(), names= state_without_threshold.keys(), color= state_without_threshold,
              width= 400,
              height = 400,    
              title=  "WITHOUT threshold",
             color_discrete_sequence=px.colors.sequential.Blues)
  fig.update_traces(textposition = 'outside', textfont_size = 15)             
  fig.update_layout(title_x = 0.5, 
                    margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                    template = 'plotly_dark'
                    )  

  st.plotly_chart(fig)

st.markdown("- __There is a little difference between rentals states if the threshold was been etablished.__")
st.markdown("- __We saw that it could reduce delays, but we should analyse more deeply a possible loss of profits.__")
st.markdown(f"- __The right trade off seems to be a threshold of {res} minutes.__")


st.header('Scope: should we enable the feature for all cars?, only Connect cars?')

fig = px.histogram(df_delay, x="delay",
                      title = 'Proportion rentals delays en relation to checkin type',
                      histnorm= 'percent',
                      color="checkin_type",
                      barmode ='group',
                      width= 800,
                      height = 500,
                      text_auto = True,
                      color_discrete_sequence=px.colors.sequential.Blues_r
                                )
                    
fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = '',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )
                      
st.plotly_chart(fig)

st.markdown("- __Connect rentals types are mostly on time (2 users of 3).__")
st.markdown("- __One user of two choosing the Mobile checkin are often delayed.__")
st.markdown(f"- __It could be a factor impacting the ended / canceled rate.__")

fig = px.histogram(df, x="2nd_rental_state",
                      title = 'Proportion of 2nd rentals states in relation to 1st rental checkin-type',
                      histnorm= 'percent',
                      color="1st_rental_checkin_type",
                      barmode ='group',
                      width= 800,
                      height = 500,
                      text_auto = True,
                      color_discrete_sequence=px.colors.sequential.Blues_r
                                )
                    
fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = '',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )
                      
st.plotly_chart(fig)

st.markdown("- __9 users of 10 choosing Mobile checkin-type end their rentals.__")
st.markdown("- __We can observe that this proportion is less important for Connect checkin-types.__")
st.markdown(f"- __This means that it could be easier for users to cancel their rental if they don't meet the owner in person.__")

st.subheader('Conclusion')

st.markdown('__130 min Threshold shold be the right compromise to satisfy users and owners, it could be applied to all checkin types.__')





    
