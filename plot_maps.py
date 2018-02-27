import pandas as pd
import numpy as np

import folium
import os

dict_icons = {22: 'credit-card', 10: 'shopping-cart', 19: 'beer'}
dict_colors = {22: 'green', 10: 'lightblue', 19: 'orange'}
dit_terminals = 'tmp_terminals'
dict_clients = 'tmp_clients'

# отрисовка маркера со значком  и цветом
def plot_marker(map, coordinate, popup = None, icon = None):
    folium.Marker(coordinate,
           popup=popup,
           icon=icon
          ).add_to(map)

# отрисовка окружности с заданным радиусом (в метрах) и цветом
def plot_circle(map, coordinate, radius = 2000, color = 'blue', fill_color = '#3186cc'):
    folium.Circle(coordinate,
        radius= radius,
        color=color,
        fill_color=fill_color,
        ).add_to(map)

def add_transactions_to_map(map, transactions_disct):
    for idx, trans in transactions_disct.iterrows():
        color = dict_colors.get(trans['mcc_common'], "pink")
        icon = dict_icons.get(trans['mcc_common'], "info-sign")
        fol_icon = folium.Icon(icon = icon, color = color)
        plot_marker(map, (trans['tran_lat'], trans['tran_lon']), icon = fol_icon, popup = trans['terminal_id'])

def plot_transactions_in_tile(df, tile_zoom_column, tile):
    transactions_disct = df[df[tile_zoom_column] == tile][['terminal_id','mcc_common', 'tran_lat', 'tran_lon']]
    map_osm = folium.Map(location=[transactions_disct.iloc[0]['tran_lat'],transactions_disct.iloc[0]['tran_lon']])
    add_transactions_to_map(map_osm, transactions_disct)
    return map_osm
   
# функция отрисовывет один терминал на карте
def plot_terminal(terminal_id, df, save = True):  
    transactions_disct = df[df['terminal_id'] == terminal_id][['terminal_id','mcc_common', 'tran_lat', 'tran_lon']].drop_duplicates()
    # центрируемся на первую транзакцию
    map_osm = folium.Map(location=[transactions_disct.iloc[0]['tran_lat'],transactions_disct.iloc[0]['tran_lon']])
    add_transactions_to_map(map_osm, transactions_disct)

    if save:
        if not os.path.exists(dit_terminals):
            os.makedirs(dit_terminals)
        map_osm.save(dit_terminals + '/' + terminal_id + '.html')
  
    return map_osm

  
# отрисовка места работы и дома + всех транзакций
def plot_one_person(person_id, df, save = True, predicted_home = None, predicted_work = None):
    transactions = df[df.customer_id == person_id]
    home_address = transactions[['home_add_lat','home_add_lon']].drop_duplicates()
    work_address = transactions[['work_add_lat','work_add_lon']].drop_duplicates()

    map_osm = folium.Map(location=[home_address.iloc[0][0],home_address.iloc[0][1]])
    tr_cnt = transactions.groupby(['terminal_id'])['terminal_id'].count().reset_index(name = 'cnt')
    transactions_disct = transactions[['terminal_id','tran_lat','tran_lon', 'mcc_common']].drop_duplicates()
    transactions_disct.dropna(inplace = True)
    home_address.dropna(inplace = True)
    work_address.dropna(inplace = True)
    
    print (home_address)
    print (work_address)
     
    # рисуем дом
    for idx, homes in home_address.iterrows():
        coord = (homes['home_add_lat'], homes['home_add_lon'])
        radius= abs(int(0.02 * 113.320 * np.cos(homes['home_add_lat']) * 1000))
        radius= 2000
        plot_marker(map_osm, coord, popup=person_id, icon = folium.Icon(color='blue',icon='home'))
        plot_circle(map_osm, coord, radius)

    # рисуем работу
    for idx, works in work_address.iterrows():
        coord = (works['work_add_lat'], works['work_add_lon'])
        radius= abs(int(0.02 * 113.320 * np.cos(works['work_add_lat']) * 1000))
        radius= 2000

        plot_marker(map_osm, coord, popup=person_id, icon = folium.Icon(color='black',icon='briefcase'))
        plot_circle(map_osm, coord, radius, color = 'black', fill_color='#3186cc') 
        
    # рисуем предсказанный дом    
    if  predicted_home != None:
        radius= 2000
        plot_marker(map_osm, predicted_home, popup=person_id, icon = folium.Icon(color='yellow',icon='home'))
        plot_circle(map_osm, predicted_home, radius, color = 'yellow') 

     # рисуем предсказанную работу
    if  predicted_work != None:

        radius= abs(int(0.02 * 113.320 * np.cos(predicted_work[0]) * 1000))
        radius= 2000
        plot_marker(map_osm, predicted_work, popup=person_id, icon = folium.Icon(color='gray',icon='briefcase'))
        plot_circle(map_osm, predicted_work, radius, color = 'gray', fill_color='#3186cc')          

    # рисуем транзакции
    add_transactions_to_map(map_osm, transactions_disct)
 
    if save:
        if not os.path.exists(dict_clients):
            os.makedirs(dict_clients)  
        map_osm.save(dict_clients + '/' + person_id + '.html')
    return map_osm		