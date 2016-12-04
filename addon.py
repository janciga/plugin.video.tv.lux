import os
import sys

sys.path.append(os.path.join (os.path.dirname(__file__), 'resources', 'lib'))
import tvlux

import xbmcprovider, xbmcaddon, xbmcutil, xbmcgui, xbmcplugin, xbmc
import util

#TODO check setting in the wiki
__scriptid__ = 'plugin.video.tv.lux.sk'
__scriptname__ = 'tvlux'
__addon__ = xbmcaddon.Addon(id=__scriptid__)
__language__ = __addon__.getLocalizedString

settings = {'downloads':__addon__.getSetting('downloads'), 'quality':__addon__.getSetting('quality')}

params = util.params()
if params == {}:
    xbmcutil.init_usage_reporting(__scriptid__)

xbmcprovider.XBMCMultiResolverContentProvider(
    tvlux.TVLuxContentProvider(tmp_dir=xbmc.translatePath(__addon__.getAddonInfo('profile'))),
    settings,
    __addon__).run(params)
