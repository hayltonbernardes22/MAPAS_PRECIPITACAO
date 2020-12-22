#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature
# from cartopy.io.shapereader import Reader
# from cartopy.feature import ShapelyFeature
import numpy as np
import pygrib
# from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
from os import listdir
from os.path import isfile, join
import urllib
import urllib2
import telepot
from PIL import Image
import glob
import shutil


def get_config_ons(flag='s'):
    if flag == 's':
        levels = [1.0001, 5.0001, 10.0001, 15.0001, 20.0001, 25.0001, 30.0001, 40.0001, 50.0001, 75.0001, 100.0001, 150.0001, 200.0001]  # niveis para chuva

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

def download00():
    y = datetime.today().strftime('%Y')
    m = datetime.today().strftime('%m')
    d = datetime.today() - timedelta(days=1)

    hh = 18

    for x in range(62):

        url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{}{}{}/00/atmos/pgrb2ap5/geavg.t00z.pgrb2a.0p50.f{}'.format(y,m,d.strftime('%d'), str(hh).zfill(3))

        urllib.urlretrieve(url, 'gefs/00z/geavg.t00z.pgrb2af{}'.format(hh))

        hh = hh + 6

def download12():
    y = datetime.today().strftime('%Y')
    m = datetime.today().strftime('%m')
    d = datetime.today() #- timedelta(days=1)

    hh = 6

    for x in range(64):

        url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{}{}{}/12/atmos/pgrb2ap5/geavg.t12z.pgrb2a.0p50.f{}'.format(y,m,d.strftime('%d'), str(hh).zfill(3))
        
        urllib.urlretrieve(url, 'gefs/12z/geavg.t12z.pgrb2af{}'.format(hh))

        hh = hh + 6

def mapa00():
    
    hh = 18

    for x in range(1, 16):
        
        print(hh)

        grbs = pygrib.open('gefs/00z/geavg.t00z.pgrb2af{}'.format(hh))
        grb = grbs.select(name='Total Precipitation')[0]
        grbs1 = pygrib.open('gefs/00z/geavg.t00z.pgrb2af{}'.format(hh + 6))
        grb1 = grbs1.select(name='Total Precipitation')[0]
        grbs2 = pygrib.open('gefs/00z/geavg.t00z.pgrb2af{}'.format(hh + 12))
        grb2 = grbs2.select(name='Total Precipitation')[0]
        grbs3 = pygrib.open('gefs/00z/geavg.t00z.pgrb2af{}'.format(hh + 18))
        grb3 = grbs3.select(name='Total Precipitation')[0]

        maxt = grb.values + grb1.values + grb2.values + grb3.values

        lats, lons = grb.latlons()

        nplots = 1

        fig = plt.figure(figsize=(10,10))

        levels, cores_ons = get_config_ons(flag='s')

        d_next = datetime.today() + timedelta(days=x)

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
            plt.title('Previsao para o dia {}/{}/{} \nRodada GEFS {}/{}/{} 00Z'.format(d_next.strftime('%d'), d_next.strftime('%m'), d_next.strftime('%y'),
            datetime.today().strftime('%d'), datetime.today().strftime('%m'), datetime.today().strftime('%y')))

            cbar = plt.colorbar(cs, ax=ax, orientation="horizontal", pad=.05, aspect=25, shrink=.8)
            cbar.set_label(label='Preciptacao [mm]', size=15)
            cbar.set_ticks(levels)

            im = plt.imread(fname=os.path.join('logo/Logo.png'))
            newax = fig.add_axes([0.60, 0.25, 0.2, 0.2], anchor='SE', zorder=+1)
            newax.imshow(im)
            newax.axis('off')

            ax.set_extent([-100,-10,-60,15])
            ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=1)
            ax.add_feature(states_provinces, edgecolor='black')
            ax.add_feature(rivers_lake_centerlines)
            ax.coastlines(resolution='10m')

        # plt.savefig('coastlines.pdf')
        plt.savefig('png_mapa/gefs/00z/{}GEFS 00z.png'.format(x), bbox_inches = 'tight',pad_inches = 0.2)

        if hh == 354:
            hh = hh + 12
        else:
            hh = hh + 24

def mapa12():
    
    hh = 6

    for x in range(1, 16):
        
        print(hh)

        grbs = pygrib.open('gefs/12z/geavg.t12z.pgrb2af{}'.format(hh))
        grb = grbs.select(name='Total Precipitation')[0]
        grbs1 = pygrib.open('gefs/12z/geavg.t12z.pgrb2af{}'.format(hh + 6))
        grb1 = grbs1.select(name='Total Precipitation')[0]
        grbs2 = pygrib.open('gefs/12z/geavg.t12z.pgrb2af{}'.format(hh + 12))
        grb2 = grbs2.select(name='Total Precipitation')[0]
        grbs3 = pygrib.open('gefs/12z/geavg.t12z.pgrb2af{}'.format(hh + 18))
        grb3 = grbs3.select(name='Total Precipitation')[0]

        maxt = grb.values + grb1.values + grb2.values + grb3.values

        lats, lons = grb.latlons()

        nplots = 1

        fig = plt.figure(figsize=(10,10))

        levels, cores_ons = get_config_ons(flag='s')

        d_next = datetime.today() + timedelta(days=x)

        for i in range(0, nplots):
            central_longitude = 0 if i == 0 else 179.99
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
            plt.title('Previsao para o dia {}/{}/{} \nRodada GEFS {}/{}/{} 12Z'.format(d_next.strftime('%d'), d_next.strftime('%m'), d_next.strftime('%y'),
            datetime.today().strftime('%d'), datetime.today().strftime('%m'), datetime.today().strftime('%y')))

            cbar = plt.colorbar(cs, ax=ax, orientation="horizontal", pad=.05, aspect=25, shrink=.8)
            cbar.set_label(label='Preciptacao [mm]', size=15)
            cbar.set_ticks(levels)

            im = plt.imread(fname=os.path.join('logo/Logo.png'))
            newax = fig.add_axes([0.60, 0.25, 0.2, 0.2], anchor='SE', zorder=+1)
            newax.imshow(im)
            newax.axis('off')

            ax.set_extent([-100,-10,-60,15])
            ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=1)
            ax.add_feature(states_provinces, edgecolor='black')
            ax.add_feature(rivers_lake_centerlines)
            ax.coastlines(resolution='10m')

        # plt.savefig('coastlines.pdf')
        plt.savefig('png_mapa/gefs/12z/{}GEFS 12z.png'.format(x), bbox_inches = 'tight',pad_inches = 0.2)
        if hh == 354:
            hh = hh + 12
        else:
            hh = hh + 24
        # hh = hh + 24 

def gif():
    # Create the frames 
    frames = []
    imgs = glob.glob("png_mapa/gefs/00z/*.png")
    for i in imgs:
        new_frame = Image.open(i)
        frames.append(new_frame)

    # Save into a GIF file that loops forever
    frames[0].save('png_mapa/gefs/00z/MAPAS_GEFS_00HRS.gif', format='GIF',
                append_images=frames[1:],
                save_all=True,
                duration=850, loop=0)

def gif12():
    # Create the frames
    frames = []
    imgs = glob.glob("png_mapa/gefs/12z/*.png")
    for i in imgs:
        new_frame = Image.open(i)
        frames.append(new_frame)

    # Save into a GIF file that loops forever
    frames[0].save('png_mapa/gefs/12z/MAPAS_GEFS_12HRS.gif', format='GIF',
                append_images=frames[1:],
                save_all=True,
                duration=850, loop=0)

def telegram():
    bot = telepot.Bot('705587356:AAHiup4yKbMykY2rts5P5aCgEKs2unLt2xk')
    
    bot.sendMessage(-338971553, "Olá, os mapas GEFS já estão disponíveis")
    bot.sendMessage(-338971553, "Segue abaixo os mapas da 00Hrs")
    bot.sendDocument(-338971553, open('png_mapa/gefs/00z/{}/{}/{}/MAPAS_GEFS_00HRS.gif'.format(
        datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')
    ), 'rb'))

def telegram12():
    bot = telepot.Bot('705587356:AAHiup4yKbMykY2rts5P5aCgEKs2unLt2xk')
    
    bot.sendMessage(-338971553, "Olá, os mapas GEFS já estão disponíveis")
    bot.sendMessage(-338971553, "Segue abaixo os mapas das 12Hrs")
    bot.sendDocument(-338971553, open('png_mapa/gefs/12z/{}/{}/{}/MAPAS_GEFS_12HRS.gif'.format(
        datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')
    ), 'rb'))

def org12():
    onlyfiles = [f for f in listdir(os.getcwd() + '/gefs/12z/') if
                         isfile(join(os.getcwd() + '/gefs/12z/', f))]

    files = [s for s in onlyfiles if 'geavg' in s]

    imagens = [f for f in listdir(os.getcwd() + '/png_mapa/gefs/12z/') if
                         isfile(join(os.getcwd() + '/png_mapa/gefs/12z/', f))]

    if not os.path.exists(os.getcwd() + '/gefs/12z/{}'.format(datetime.today().strftime('%Y'))):
        os.mkdir(os.getcwd() + '/gefs/12z/{}'.format(datetime.today().strftime('%Y')))

    if not os.path.exists(os.getcwd() + '/gefs/12z/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'))):
        os.mkdir(os.getcwd() + '/gefs/12z/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m')))
    
    if not os.path.exists(os.getcwd() + '/gefs/12z/{}/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d'))):
        os.mkdir(os.getcwd() + '/gefs/12z/{}/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')))

    for f in files:
        shutil.move(os.getcwd() + '/gefs/12z/' + f,
        os.getcwd() + '/gefs/12z/{}/{}/{}/'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')) + f)
    
    if not os.path.exists(os.getcwd() + '/png_mapa/gefs/12z/{}'.format(datetime.today().strftime('%Y'))):
        os.mkdir(os.getcwd() + '/png_mapa/gefs/12z/{}'.format(datetime.today().strftime('%Y')))

    if not os.path.exists(os.getcwd() + '/png_mapa/gefs/12z/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'))):
        os.mkdir(os.getcwd() + '/png_mapa/gefs/12z/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m')))
    
    if not os.path.exists(os.getcwd() + '/png_mapa/gefs/12z/{}/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d'))):
        os.mkdir(os.getcwd() + '/png_mapa/gefs/12z/{}/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')))

    for img in imagens:
        shutil.move(os.getcwd() + '/png_mapa/gefs/12z/' + img,
        os.getcwd() + '/png_mapa/gefs/12z/{}/{}/{}/'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')) + img)

def org00():
    onlyfiles = [f for f in listdir(os.getcwd() + '/gefs/00z/') if
                         isfile(join(os.getcwd() + '/gefs/00z/', f))]

    files = [s for s in onlyfiles if 'geavg' in s]

    imagens = [f for f in listdir(os.getcwd() + '/png_mapa/gefs/00z/') if
                         isfile(join(os.getcwd() + '/png_mapa/gefs/00z/', f))]

    if not os.path.exists(os.getcwd() + '/gefs/00z/{}'.format(datetime.today().strftime('%Y'))):
        os.mkdir(os.getcwd() + '/gefs/00z/{}'.format(datetime.today().strftime('%Y')))

    if not os.path.exists(os.getcwd() + '/gefs/00z/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'))):
        os.mkdir(os.getcwd() + '/gefs/00z/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m')))
    
    if not os.path.exists(os.getcwd() + '/gefs/00z/{}/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d'))):
        os.mkdir(os.getcwd() + '/gefs/00z/{}/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')))

    #MOVENDO ARQUIVOS DOS MAPAS
    for f in files:
        shutil.move(os.getcwd() + '/gefs/00z/' + f,
        os.getcwd() + '/gefs/00z/{}/{}/{}/'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')) + f)

    if not os.path.exists(os.getcwd() + '/png_mapa/gefs/00z/{}'.format(datetime.today().strftime('%Y'))):
        os.mkdir(os.getcwd() + '/png_mapa/gefs/00z/{}'.format(datetime.today().strftime('%Y')))

    if not os.path.exists(os.getcwd() + '/png_mapa/gefs/00z/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'))):
        os.mkdir(os.getcwd() + '/png_mapa/gefs/00z/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m')))
    
    if not os.path.exists(os.getcwd() + '/png_mapa/gefs/00z/{}/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d'))):
        os.mkdir(os.getcwd() + '/png_mapa/gefs/00z/{}/{}/{}'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')))

    #MOVENDO AS IMAGENS DOS MAPAS
    for img in imagens:
        shutil.move(os.getcwd() + '/png_mapa/gefs/00z/' + img,
        os.getcwd() + '/png_mapa/gefs/00z/{}/{}/{}/'.format(datetime.today().strftime('%Y'), datetime.today().strftime('%m'), datetime.today().strftime('%d')) + img)

def main():
    while True:
        now = datetime.now()
        if now.hour == 7 and now.minute == 00:
            for x in range(999*999):
                try:
                    download00()
                    mapa00()
                    gif()
                    org00()
                    telegram()
                    break
                except Exception as e:
                    print('Error %s' %e)

        if now.hour == 14 and now.minute == 30:
            for x in range(999*999):
                try:
                    download12()
                    mapa12()
                    gif12()
                    org12()
                    telegram12()
                    break
                except Exception as e:
                    print('Error %s' %e)

if __name__ == "__main__":
    main()
    #download00()
    #mapa00()
    #gif()
    #org00()
    #telegram()
    #download12()
    #mapa12()
    #gif12()
    #org12()
    #telegram12()
