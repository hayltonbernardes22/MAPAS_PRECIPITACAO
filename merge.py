#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
import time
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import numpy as np
import pygrib
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
from os import listdir
from os.path import isfile, join
import urllib
import telepot
from PIL import Image
import glob

def get_config_ons(flag='s'):
    if flag == 's':
        levels = [1, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200]  # niveis para chuva

    cores_ons = [(255.0 / 255.0, 255.0 / 255.0, 255.0 / 255.0),
                 (180.0 / 255.0, 240.0 / 255.0, 250.0 / 255.0),
                 (120.0 / 255.0, 188.0 / 255.0, 255.0 / 255.0),
                 (40.0 / 255.0, 130.0 / 255.0, 240.0 / 255.0),
                 (20.0 / 255.0, 100.0 / 255.0, 210.0 / 255.0),
                 (103.0 / 255.0, 254.0 / 255.0, 133.0 / 255.0),
                 (24.0 / 255.0, 215.0 / 255.0, 6.0 / 255.0),
                 (30.0 / 255.0, 180.0 / 255.0, 30.0 / 255.0),
                 (255.0 / 255.0, 232.0 / 255.0, 120.0 / 255.0),
                 (255.0 / 255.0, 192.0 / 255.0, 60.0 / 255.0),
                 (255.0 / 255.0, 96.0 / 255.0, 0.0 / 255.0),
                 (225.0 / 255.0, 20.0 / 255.0, 0.0 / 255.0),
                 (251.0 / 255.0, 94.0 / 255.0, 107.0 / 255.0),
                 (170.0 / 255.0, 170.0 / 255.0, 170.0 / 255.0)
                 ]  # Escala de cores ONS
    return levels, cores_ons

def download():
    data = datetime.today() - timedelta(days = 1, hours= datetime.today().hour, minutes=datetime.today().minute, seconds= datetime.today().second)

    data = data + timedelta(hours=10)

    for x in range(24):
        y = data.strftime('%Y')
        m = data.strftime('%m')
        d = data.strftime('%d')
        h = data.strftime('%H')
        
        url = 'http://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/HOURLY/{}/{}/{}/MERGE_CPTEC_{}{}{}{}.grib2'.format(y,m,d, y,m,d, str(h).zfill(2))
        
        print(url)

        urllib.urlretrieve(url, 'merge/MERGE_GPM_early_{}{}{}{}.grib2'.format(y,m,d, str(h).zfill(2)))
        
        data = data + timedelta(hours=1)
        
def mapa():
    data = datetime.today() - timedelta(days = 1, hours= datetime.today().hour, minutes=datetime.today().minute, seconds= datetime.today().second)

    data = data + timedelta(hours=10)

    grib = [f for f in listdir(os.getcwd() + '/merge') if
                         isfile(join(os.getcwd() +'/merge', f))]
    
    files = [s for s in grib if "MERGE" in s]

    maxt = 0

    for x in range(24):
        print(data.strftime('%d/%m/%Y %H:%M'))

        y = data.strftime('%Y')
        m = data.strftime('%m')
        d = data.strftime('%d')
        h = data.strftime('%H')

        grbs = pygrib.open('merge/MERGE_GPM_early_{}{}{}{}.grib2'.format(y,m,d, str(h).zfill(2)))
        grb = grbs.select(name='Precipitation')[0]
        maxt = maxt + grb.values
        lats, lons = grb.latlons()

        data = data + timedelta(hours=1)

    data = datetime.today() - timedelta(days = 1)

    nplots = 1

    fig = plt.figure(figsize=(10,10))

    levels, cores_ons = get_config_ons(flag='s')

    for i in range(0, nplots):
            central_longitude = 0 if i == 0 else 180
            rivers_lake_centerlines = cfeature.NaturalEarthFeature(category = 'physical', name = 'rivers_lake_centerlines',
            scale = '10m', facecolor = 'none', edgecolor = 'gray', alpha=0.5)
            states_provinces = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_1_states_provinces_lines',
                scale='50m',
                facecolor='none')
            ax = fig.add_subplot(nplots, 1, i+1,
                                projection=ccrs.PlateCarree(
                                            central_longitude=central_longitude))
            
            cs = plt.contourf(lons, lats, maxt, levels=levels, colors=cores_ons, extend='both')
            plt.title('Chuva Observada (MERGE - CPTEC/INPE)\nPeriodo: 12z {}/{}/{} ate 12z {}/{}/{}'.format(
                data.strftime('%d'), data.strftime('%m'), data.strftime('%y'),
                datetime.today().strftime('%d'), datetime.today().strftime('%m'), datetime.today().strftime('%y')))

            cbar = plt.colorbar(cs, ax=ax, orientation="horizontal", pad=.05, aspect=25, shrink=.6)
            cbar.set_label(label='Preciptacao [mm]', size=15)
            cbar.set_ticks(levels)

            im = plt.imread(fname=os.path.join('logo/Logo.png'))
            newax = fig.add_axes([0.55, 0.25, 0.2, 0.2], anchor='SE', zorder=+1)
            newax.imshow(im)
            newax.axis('off')

            ax.set_extent([-82,-33,-50,10])
            ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=1)
            ax.add_feature(states_provinces, edgecolor='black')
            ax.add_feature(rivers_lake_centerlines)
            ax.coastlines(resolution='10m')

    # plt.savefig('coastlines.pdf')
    plt.savefig(os.getcwd() + '/png_mapa/merge/MERGE_{}{}{}.png'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'),datetime.today().strftime('%d')), bbox_inches = 'tight',pad_inches = 0.2)

def telegram():
    bot = telepot.Bot('705587356:AAHiup4yKbMykY2rts5P5aCgEKs2unLt2xk')
    
    bot.sendMessage(-338971553, "Olá, o mapa do MERGE já está disponíveis")
    bot.sendMessage(-338971553, "Segue abaixo o mapa")
    bot.sendPhoto(-338971553, open(os.getcwd()+'/png_mapa/merge/MERGE_{}{}{}.png'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'),datetime.today().strftime('%d')), 'rb'))

def main():
    while True:
        now = datetime.now()
        if now.hour == 12 and now.minute == 15:
            for x in range(999*999):
                try:
                    download()
                    mapa()
                    telegram()
                    time.sleep(9999)
                    break
                except Exception as e:
                    print(e)
                    
if __name__ == "__main__":
    main()
    #download()
    #mapa()
    #telegram()
    pass