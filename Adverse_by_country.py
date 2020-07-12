#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 10:17:41 2020

@author: jonyoung
"""


# import what we need
import json
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt

# set base url that will be used in all API queries
base_url = 'https://api.fda.gov/drug/event.json?'

# get the number of adverse events in each country
with urllib.request.urlopen(base_url + 'count=occurcountry') as url:
    total_adverse_events_by_country= json.loads(url.read().decode())['results']
    
# take a list of countries with more than 10,000 events reported for valid statistics
countries_counts = list(filter(lambda elem: elem['count'] > 10000, total_adverse_events_by_country))
countries = list(map(lambda elem: elem['term'], countries_counts))
total_events = list(map(lambda elem: elem['count'], countries_counts))

# store countries and total adverse events in a DF
events = pd.DataFrame(countries, columns=['country']) 
events['total events'] = pd.Series(total_events)

# list of other fields to populate the DF with
serious_fields = ['serious', 'seriousnesscongenitalanomali', 'seriousnessdeath', 'seriousnessdisabling', 
                  'seriousnesshospitalization', 'seriousnesslifethreatening', 'seriousnessother']

# count instances of each serious field for each country
for field in serious_fields :
    
    
    counts = []
    for country in countries :
        
        print(field)
        print(country)
        
        # query the API to get the count json
        with urllib.request.urlopen(base_url + 'search=occurcountry:' + country + '&count='+field) as url:
            
            event_count_json=json.loads(url.read().decode())
            
        # extract the count and append
        count_dict = list(filter(lambda elem: elem['term'] == 1, event_count_json['results']))[0]
        count = count_dict['count']
        counts.append(count)
        
    # add the list of counts as a new column to the DF
    events[field] = pd.Series(counts)

countries = events['country'].values

# normalise serious events by total events
events['serious'] = events['serious'] / events['total events']
    
# normalise types of serious events by sum of types of serious events overall serious event
# as total serious events != sum of types of serious events
events['total serious event types'] = events[serious_fields[1:]].sum(axis=1)
for serious_field in serious_fields[1:] :
    
    events[serious_field] = events[serious_field] / events['total serious event types']
    
# plot a pie chart of the share of each type of serious event for each country
labels = serious_fields[1:]
event_freqs = events[labels].values
for i, country in enumerate(countries) :
    
    fig1, ax1 = plt.subplots()
    ax1.pie(event_freqs[i, :], autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title('serious event breakdown in country ' + country)
    plt.legend(labels, loc='lower center', ncol=2)
    plt.show()
    
# calculate mean and standard deviation of frequencies of each serious event type across countries
serious_event_frequencies = events[serious_fields[1:]]
stds = serious_event_frequencies.std(axis=0)
means = serious_event_frequencies.mean(axis=0)
summary_stats = pd.concat([means, stds], axis=1)


    



        
    

    



