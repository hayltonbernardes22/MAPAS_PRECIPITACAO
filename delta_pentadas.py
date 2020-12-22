#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.colors
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
import telepot
from PIL import Image
import glob
from fpdf import FPDF
import time
import sys

#Não mexa nessa função a menos que haja bug no nível
def get_config_ons(flag):
    #Cor e níveis para mapa de preciptação
    if flag == 's':
        levels = [1.0001,
         5.0001,
          10.0001,
           15.0001,
            20.0001,
             25.0001,
              30.0001,
               40.0001,
                50.0001,
                 75.0001,
                  100.0001,
                   150.0001,
                    200.0001]  # niveis para chuva

        cores_ons = [
                  #Red   Green           Blue
        		 (255.0 / 255.0, 255.0 / 255.0, 255.0 / 255.0),
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

    #Cor e níveis para mapa de diferença
    if flag == 'd':
        levels = [-100.0001,
         -75.0001,
          -50.0001,
           -25.0001,
            -20.0001,
             -15.0001,
             -10.0001,
              -5.0001,
               5.0001,
               10.0001,
                15.0001,
                20.0001,
                 25.0001,
                   50.0001,
                    75.0001,
                     100.0001
                     ]  # niveis para chuva

        cores_ons = [
                  #Red   Green      Blue
                 (64.0 / 255.0, 0 / 255.0, 0 / 255.0),
                 (107.0 / 255.0, 14.0 / 255.0, 14.0 / 255.0),
                 (148.0 / 255.0, 35.0 / 255.0, 35.0 / 255.0),
                 (179.0 / 255.0, 62.0 / 255.0, 62.0 / 255.0),
                 (201.0 / 255.0, 85.0 / 255.0, 85.0 / 255.0),
                 (240.0 / 255.0, 117.0 / 255.0, 117.0 / 255.0),
                 (255.0 / 255.0, 150.0 / 255.0, 150.0 / 255.0),
                 (255.0 / 255.0, 184.0 / 255.0, 184.0 / 255.0),

                 (255.0 / 255.0, 255.0 / 255.0, 255.0 / 255.0),

                 (184.0 / 255.0, 184.0 / 255.0, 255.0 / 255.0),
                 (150.0 / 255.0, 150.0 / 255.0, 255.0 / 255.0),
                 (117.0 / 255.0, 117.0 / 255.0, 240.0 / 255.0),
                 (85.0 / 255.0, 85.0 / 255.0, 201.0 / 255.0),
                 (62.0 / 255.0, 62.0 / 255.0, 179.0 / 255.0),
                 (35.0 / 255.0, 35.0 / 255.0, 148.0 / 255.0),
                 (14.0 / 255.0, 14.0 / 255.0, 107.0 / 255.0),
                 ( 0 / 255.0, 0 / 255.0, 64.0 / 255.0),

                 ]  # Escala de cores ONS
        return levels, cores_ons

def mapa_delta():
    
    hoje = datetime.today()
    ontem = datetime.today() - timedelta(days=1)

    for x in range(3):
        if x == 0:
            h = 18
            d1 = datetime.today() + timedelta(days=1)
            d1_ = d1 + timedelta(days=3)
        elif x == 1:
            h = 114
            d2 = datetime.today() + timedelta(days=5)
            d2_ = d2 + timedelta(days=4)
        else:
            h = 234
            d3 = datetime.today() + timedelta(days=10)
            d3_ = d3 + timedelta(days=3)
        
        max_val_hoje = 0
        max_val_ontem = 0
        
        if x == 1:
            for k in range(20):
                grbs_hoje = pygrib.open('gefs/00z/{}/{}/{}/geavg.t00z.pgrb2af{}'.format(hoje.strftime('%Y'), hoje.strftime('%m'), hoje.strftime('%d'), h))
                grb_hoje = grbs_hoje.select(name='Total Precipitation')[0]

                max_val_hoje = max_val_hoje + grb_hoje.values

                # lt, ln = grb_hoje.latlons()
                # lats, lons = np.array(lt), np.array(ln)

                grbs_ontem = pygrib.open('gefs/00z/{}/{}/{}/geavg.t00z.pgrb2af{}'.format(ontem.strftime('%Y'), ontem.strftime('%m'), ontem.strftime('%d'), h+24))
                grb_ontem = grbs_ontem.select(name='Total Precipitation')[0]

                max_val_ontem = max_val_ontem + grb_ontem.values

                lt, ln = grb_ontem.latlons()
                lats, lons = np.array(lt), np.array(ln)

                h = h + 6

        for y in range(16):

            grbs_hoje = pygrib.open('gefs/00z/{}/{}/{}/geavg.t00z.pgrb2af{}'.format(hoje.strftime('%Y'), hoje.strftime('%m'), hoje.strftime('%d'), h))
            grb_hoje = grbs_hoje.select(name='Total Precipitation')[0]

            max_val_hoje = max_val_hoje + grb_hoje.values

            # lt, ln = grb_hoje.latlons()
            # lats, lons = np.array(lt), np.array(ln)
            
            grbs_ontem = pygrib.open('gefs/00z/{}/{}/{}/geavg.t00z.pgrb2af{}'.format(ontem.strftime('%Y'), ontem.strftime('%m'), ontem.strftime('%d'), h+24))
            grb_ontem = grbs_ontem.select(name='Total Precipitation')[0]

            max_val_ontem = max_val_ontem + grb_ontem.values
            
            lt, ln = grb_ontem.latlons()
            lats, lons = np.array(lt), np.array(ln)

            h = h + 6

        maxt = max_val_hoje - max_val_ontem

        nplots = 1

        fig = plt.figure(figsize=(10,10))

        levels, diferenca = get_config_ons(flag='d')

        for i in range(0, nplots):
            central_longitude = 0 if i == 0 else 180
            rivers_lake_centerlines = cfeature.NaturalEarthFeature(category = 'physical', name = 'rivers_lake_centerlines',
            scale = '10m', facecolor = 'none', edgecolor = 'gray', alpha=0.5)
            states_provinces = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_1_states_provinces_lines',
                scale='50m',
                facecolor='none')
            ax = fig.add_subplot(nplots, 1, i+1,projection=ccrs.PlateCarree(central_longitude=central_longitude))
                
            cs = plt.contourf(lons, lats, maxt, levels=levels, colors=diferenca, extend='both', alpha=1)
            if x == 0:
                plt.title(u'Variação de proj. dos dias {}/{}/{} a {}/{}/{} GEFS 00Z'.format(
                    d1.strftime('%d'),d1.strftime('%m'),d1.strftime('%y'), d1_.strftime('%d'),d1_.strftime('%m'),d1_.strftime('%y')))
            elif x == 1:
                plt.title(u'Variação de proj. dos dias {}/{}/{} a {}/{}/{} GEFS 00Z'.format(
                    d2.strftime('%d'),d2.strftime('%m'),d2.strftime('%y'), d2_.strftime('%d'),d2_.strftime('%m'),d2_.strftime('%y')))
            else:
                plt.title(u'Variação de proj. dos dias {}/{}/{} a {}/{}/{} GEFS 00Z'.format(
                    d3.strftime('%d'),d3.strftime('%m'),d3.strftime('%y'), d3_.strftime('%d'),d3_.strftime('%m'),d3_.strftime('%y')))

            cbar = plt.colorbar(cs, ax=ax, orientation="horizontal", pad=.05, aspect=25, shrink=.8)
            cbar.set_label(label=u'Preciptação [mm]', size=15)
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
            plt.savefig('delta/Pentada Delta {}.png'.format(x), bbox_inches = 'tight',pad_inches = 0.2)

def mapa_gefs_00_ontem():
    
    ontem = datetime.today() - timedelta(days=1)

    for x in range(3):
        if x == 0:
            h = 42
            d1 = ontem + timedelta(days=2)
            d1_ = d1 + timedelta(days=4)
        elif x == 1:
            h = 138
            d2 = ontem + timedelta(days=7)
            d2_ = d2 + timedelta(days=4)
        else:
            h = 258
            d3 = ontem + timedelta(days=12)
            d3_ = d3 + timedelta(days=4)
        
        max_val_ontem = 0

        if x == 0:
            for y in range(16):
                grbs_ontem = pygrib.open('gefs/00z/{}/{}/{}/geavg.t00z.pgrb2af{}'.format(ontem.strftime('%Y'), ontem.strftime('%m'), ontem.strftime('%d'), h))
                grb_ontem = grbs_ontem.select(name='Total Precipitation')[0]

                max_val_ontem = max_val_ontem + grb_ontem.values
                maxt = max_val_ontem

                lt, ln = grb_ontem.latlons()
                lats, lons = np.array(lt), np.array(ln)

                h = h + 6
        else:
            for y in range(20):
                grbs_ontem = pygrib.open('gefs/00z/{}/{}/{}/geavg.t00z.pgrb2af{}'.format(ontem.strftime('%Y'), ontem.strftime('%m'), ontem.strftime('%d'), h))
                grb_ontem = grbs_ontem.select(name='Total Precipitation')[0]

                max_val_ontem = max_val_ontem + grb_ontem.values
                maxt = max_val_ontem

                lt, ln = grb_ontem.latlons()
                lats, lons = np.array(lt), np.array(ln)

                h = h + 6

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
            ax = fig.add_subplot(nplots, 1, i+1,projection=ccrs.PlateCarree(central_longitude=central_longitude))
                
            cs = plt.contourf(lons, lats, maxt, levels=levels, colors=cores_ons, extend='both')
            if x == 0:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 00h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    1, ontem.strftime('%d'), ontem.strftime('%m'), ontem.strftime('%Y'),
                    d1.strftime('%d'),d1.strftime('%m'),d1.strftime('%Y'), d1_.strftime('%d'),d1_.strftime('%m'),d1_.strftime('%Y')))
            elif x == 1:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 00h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    2, ontem.strftime('%d'), ontem.strftime('%m'), ontem.strftime('%Y'),
                    d2.strftime('%d'),d2.strftime('%m'),d2.strftime('%Y'), d2_.strftime('%d'),d2_.strftime('%m'),d2_.strftime('%Y')))
            else:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 00h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    3, ontem.strftime('%d'), ontem.strftime('%m'), ontem.strftime('%Y'),
                    d3.strftime('%d'),d3.strftime('%m'),d3.strftime('%Y'), d3_.strftime('%d'),d3_.strftime('%m'),d3_.strftime('%Y')))

            cbar = plt.colorbar(cs, ax=ax, orientation="horizontal", pad=.05, aspect=25, shrink=.8)
            cbar.set_label(label=u'Preciptação [mm]', size=15)
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
            plt.savefig('delta/Pentada D-1 GEFS {}.png'.format(x), bbox_inches = 'tight',pad_inches = 0.2)

def mapa_gefs_00_hoje():
    
    hoje = datetime.today()

    for x in range(3):
        if x == 0:
            h = 18
            d1 = hoje + timedelta(days=1)
            d1_ = d1 + timedelta(days=4)
        elif x == 1:
            h = 138
            d2 = hoje + timedelta(days=6)
            d2_ = d2 + timedelta(days=4)
        else:
            h = 258
            d3 = hoje + timedelta(days=11)
            d3_ = d3 + timedelta(days=4)
        
        max_val_hoje = 0

        for y in range(20):

            grbs_hoje = pygrib.open('gefs/00z/{}/{}/{}/geavg.t00z.pgrb2af{}'.format(hoje.strftime('%Y'), hoje.strftime('%m'), hoje.strftime('%d'), h))
            grb_hoje = grbs_hoje.select(name='Total Precipitation')[0]

            max_val_hoje = max_val_hoje + grb_hoje.values
            maxt = max_val_hoje

            lt, ln = grb_hoje.latlons()
            lats, lons = np.array(lt), np.array(ln)

            h = h + 6

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
            ax = fig.add_subplot(nplots, 1, i+1,projection=ccrs.PlateCarree(central_longitude=central_longitude))
                
            cs = plt.contourf(lons, lats, maxt, levels=levels, colors=cores_ons, extend='both')
            if x == 0:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 00h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    1, hoje.strftime('%d'), hoje.strftime('%m'), hoje.strftime('%Y'),
                    d1.strftime('%d'),d1.strftime('%m'),d1.strftime('%Y'), d1_.strftime('%d'),d1_.strftime('%m'),d1_.strftime('%Y')))
            elif x == 1:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 00h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    2, hoje.strftime('%d'), hoje.strftime('%m'), hoje.strftime('%Y'),
                    d2.strftime('%d'),d2.strftime('%m'),d2.strftime('%Y'), d2_.strftime('%d'),d2_.strftime('%m'),d2_.strftime('%Y')))
            else:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 00h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    3, hoje.strftime('%d'), hoje.strftime('%m'), hoje.strftime('%Y'),
                    d3.strftime('%d'),d3.strftime('%m'),d3.strftime('%Y'), d3_.strftime('%d'),d3_.strftime('%m'),d3_.strftime('%Y')))

            cbar = plt.colorbar(cs, ax=ax, orientation="horizontal", pad=.05, aspect=25, shrink=.8)
            cbar.set_label(label=u'Preciptação [mm]', size=15)
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
            plt.savefig('delta/Pentada D GEFS {}.png'.format(x), bbox_inches = 'tight',pad_inches = 0.2)

def mapa_gefs_12_hoje():
    
    hoje = datetime.today()

    for x in range(3):
        if x == 0:
            h = 6
            d1 = hoje + timedelta(days=1)
            d1_ = d1 + timedelta(days=4)
        elif x == 1:
            h = 120
            d2 = hoje + timedelta(days=6)
            d2_ = d2 + timedelta(days=4)
        else:
            h = 246
            d3 = hoje + timedelta(days=11)
            d3_ = d3 + timedelta(days=4)
        
        max_val_hoje = 0

        for y in range(20):

            grbs_hoje = pygrib.open('gefs/12z/{}/{}/{}/geavg.t12z.pgrb2af{}'.format(hoje.strftime('%Y'), hoje.strftime('%m'), hoje.strftime('%d'), h))
            grb_hoje = grbs_hoje.select(name='Total Precipitation')[0]

            max_val_hoje = max_val_hoje + grb_hoje.values
            maxt = max_val_hoje

            lt, ln = grb_hoje.latlons()
            lats, lons = np.array(lt), np.array(ln)

            h = h + 6

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
            ax = fig.add_subplot(nplots, 1, i+1,projection=ccrs.PlateCarree(central_longitude=central_longitude))
                
            cs = plt.contourf(lons, lats, maxt, levels=levels, colors=cores_ons, extend='both')
            if x == 0:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 12h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    1, hoje.strftime('%d'), hoje.strftime('%m'), hoje.strftime('%Y'),
                    d1.strftime('%d'),d1.strftime('%m'),d1.strftime('%Y'), d1_.strftime('%d'),d1_.strftime('%m'),d1_.strftime('%Y')))
            elif x == 1:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 12h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    2, hoje.strftime('%d'), hoje.strftime('%m'), hoje.strftime('%Y'),
                    d2.strftime('%d'),d2.strftime('%m'),d2.strftime('%Y'), d2_.strftime('%d'),d2_.strftime('%m'),d2_.strftime('%Y')))
            else:
                plt.title(u'{}ª Pêntada Rodada GEFS {}/{}/{} 12h\nPrevisão de {}/{}/{} a {}/{}/{}'.format(
                    3, hoje.strftime('%d'), hoje.strftime('%m'), hoje.strftime('%Y'),
                    d3.strftime('%d'),d3.strftime('%m'),d3.strftime('%Y'), d3_.strftime('%d'),d3_.strftime('%m'),d3_.strftime('%Y')))

            cbar = plt.colorbar(cs, ax=ax, orientation="horizontal", pad=.05, aspect=25, shrink=.8)
            cbar.set_label(label=u'Preciptação [mm]', size=15)
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
            plt.savefig('delta/Pentada 12h D GEFS {}.png'.format(x), bbox_inches = 'tight',pad_inches = 0.2)

def mapa_delta_12_00():
    
    hoje = datetime.today()

    for x in range(3):
        if x == 0:
            h = 18
            hh = 6
            d1 = datetime.today() + timedelta(days=1)
            d1_ = d1 + timedelta(days=4)
        elif x == 1:
            h = 138
            hh = 126
            d2 = datetime.today() + timedelta(days=6)
            d2_ = d2 + timedelta(days=4)
        else:
            h = 258
            hh = 246
            d3 = datetime.today() + timedelta(days=11)
            d3_ = d3 + timedelta(days=4)
        
        max_val_hoje_00 = 0
        max_val_hoje_12 = 0

        for y in range(20):

            grbs_hoje_00 = pygrib.open('gefs/00z/{}/{}/{}/geavg.t00z.pgrb2af{}'.format(hoje.strftime('%Y'), hoje.strftime('%m'), hoje.strftime('%d'), h))
            grb_hoje_00 = grbs_hoje_00.select(name='Total Precipitation')[0]

            max_val_hoje_00 = max_val_hoje_00 + grb_hoje_00.values

            grbs_hoje_12 = pygrib.open('gefs/12z/{}/{}/{}/geavg.t12z.pgrb2af{}'.format(hoje.strftime('%Y'), hoje.strftime('%m'), hoje.strftime('%d'), hh))
            grb_hoje_12 = grbs_hoje_12.select(name='Total Precipitation')[0]

            max_val_hoje_12 = max_val_hoje_12 + grb_hoje_12.values
            
            lt, ln = grb_hoje_00.latlons()
            lats, lons = np.array(lt), np.array(ln)

            h = h + 6
            hh = hh + 6

        maxt = max_val_hoje_12 - max_val_hoje_00

        nplots = 1

        fig = plt.figure(figsize=(10,10))
        fig.subplots_adjust(wspace=0.3)

        levels, diferenca = get_config_ons(flag='d')

        for i in range(0, nplots):
            central_longitude = 0 if i == 0 else 180
            rivers_lake_centerlines = cfeature.NaturalEarthFeature(category = 'physical', name = 'rivers_lake_centerlines',
            scale = '10m', facecolor = 'none', edgecolor = 'gray', alpha=0.5)
            states_provinces = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_1_states_provinces_lines',
                scale='50m',
                facecolor='none')
            ax = fig.add_subplot(nplots, 1, i+1,projection=ccrs.PlateCarree(central_longitude=central_longitude))
                
            cs = plt.contourf(lons, lats, maxt, levels=levels, colors=diferenca, extend='both')
            if x == 0:
                plt.title(u'Variação de proj. dos dias {}/{}/{} a {}/{}/{}\nGEFS 12Z - GEFS 00Z'.format(
                    d1.strftime('%d'),d1.strftime('%m'),d1.strftime('%y'), 
                    d1_.strftime('%d'),d1_.strftime('%m'),d1_.strftime('%y')))
            elif x == 1:
                plt.title(u'Variação de proj. dos dias {}/{}/{} a {}/{}/{}\nGEFS 12Z - GEFS 00Z'.format(
                    d2.strftime('%d'),d2.strftime('%m'),d2.strftime('%y'), 
                    d2_.strftime('%d'),d2_.strftime('%m'),d2_.strftime('%y')))
            else:
                plt.title(u'Variação de proj. dos dias {}/{}/{} a {}/{}/{}\nGEFS 12Z - GEFS 00Z'.format(
                    d3.strftime('%d'),d3.strftime('%m'),d3.strftime('%y'), 
                    d3_.strftime('%d'),d3_.strftime('%m'),d3_.strftime('%y')))

            cbar = plt.colorbar(cs, ax=ax, orientation="horizontal", pad=.05, aspect=25, shrink=.8)
            cbar.set_label(label=u'Preciptação [mm]', size=15)
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
            plt.savefig('delta/Pentada Delta 12-00 {}.png'.format(x), bbox_inches = 'tight',pad_inches = 0.2)

def pdf00_00():
    pdf = FPDF(orientation='L', unit='mm', format=(380,300))
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.text(100, 10, u'Projeção de pentadas 00z e 00z')
    pdf.image('delta/Pentada D-1 GEFS 0.png', x=1, y=18, w=100)
    pdf.image('delta/Pentada D-1 GEFS 1.png', x=98, y=18, w=100)
    pdf.image('delta/Pentada D-1 GEFS 2.png', x=196, y=18, w=100)

    pdf.image('delta/Pentada D GEFS 0.png', x=1, y=140, w=100)
    pdf.image('delta/Pentada D GEFS 1.png', x=98, y=140, w=100)
    pdf.image('delta/Pentada D GEFS 2.png', x=196, y=140, w=100)

    pdf.image('delta/Pentada Delta 0.png', x=1, y=260, w=100)
    pdf.image('delta/Pentada Delta 1.png', x=98, y=260, w=100)
    pdf.image('delta/Pentada Delta 2.png', x=196, y=260, w=100)

    pdf.output('delta/Diferenca de pentadas entre D e D-1.pdf')

def pdf12_00():
    pdf = FPDF(orientation='L', unit='mm', format=(380,300))
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.text(100, 10, u'Projeção de pentadas 00z e 12z')
    pdf.image('delta/Pentada D GEFS 0.png', x=1, y=18, w=100)
    pdf.image('delta/Pentada D GEFS 1.png', x=98, y=18, w=100)
    pdf.image('delta/Pentada D GEFS 2.png', x=196, y=18, w=100)

    pdf.image('delta/Pentada 12h D GEFS 0.png', x=1, y=140, w=100)
    pdf.image('delta/Pentada 12h D GEFS 1.png', x=98, y=140, w=100)
    pdf.image('delta/Pentada 12h D GEFS 2.png', x=196, y=140, w=100)

    pdf.image('delta/Pentada Delta 12-00 0.png', x=1, y=260, w=100)
    pdf.image('delta/Pentada Delta 12-00 1.png', x=98, y=260, w=100)
    pdf.image('delta/Pentada Delta 12-00 2.png', x=196, y=260, w=100)

    pdf.output('delta/Diferenca de pentadas entre 12z e 00z.pdf')

def telegram00():
    bot = telepot.Bot('705587356:AAHiup4yKbMykY2rts5P5aCgEKs2unLt2xk')
    
    bot.sendMessage(-338971553, "Olá, os mapas de diferença do GEFS 00z-00z já estão disponíveis")
    bot.sendMessage(-338971553, "Segue abaixo os mapas")
    bot.sendDocument(-338971553, open('delta/Diferenca de pentadas entre D e D-1.pdf', 'rb'))

def telegram12():
    bot = telepot.Bot('705587356:AAHiup4yKbMykY2rts5P5aCgEKs2unLt2xk')
    
    bot.sendMessage(-338971553, "Olá, os mapas de diferença do GEFS 00z-12z já estão disponíveis")
    bot.sendMessage(-338971553, "Segue abaixo os mapas")
    bot.sendDocument(-338971553, open('delta/Diferenca de pentadas entre 12z e 00z.pdf', 'rb'))

def timer():
    while True:
        now = datetime.today()
        #sys.stdout.write('\r {}:{}'.format(now.hour,now.minute))
        if now.hour == 7 and now.minute == 30:
            for x in range(999*999):
                try:
                    mapa_gefs_00_hoje()
                    mapa_gefs_00_ontem()
                    mapa_delta()
                    pdf00_00()
                    telegram00()
                    time.sleep(60)
                    break
                except Exception as e:
                    print(e)
        
        if now.hour == 14 and now.minute == 45:
            for x in range(999*999):
                try:
                    mapa_gefs_12_hoje()
                    mapa_delta_12_00()
                    pdf12_00()
                    telegram12()
                    time.sleep(60)
                    break
                except Exception as e:
                    print(e)
        
if __name__ == "__main__":
    timer()
    #mapa_gefs_00_hoje()
    #mapa_gefs_00_ontem()
    #mapa_delta()
    #pdf00_00()
    #telegram00()
    #mapa_gefs_12_hoje()
    #mapa_delta_12_00()
    #pdf12_00()
    #telegram12()