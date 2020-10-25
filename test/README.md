# Testing and debugging this Kodi addon on Ubuntu

- Install KODI on Ubuntu: https://kodi.wiki/view/HOW-TO:Install_Kodi_for_Linux
- Start kodi from cli (kodi --debug)
- Install CZ SK repository into kodi: https://kodi-czsk.github.io/repository/
- Install TV Lux plugin (it will install all needed dependencies)
- Delete the installed TV Lux plugin from ~/.kodi/addons/
- Clone the addon sources directly into ~/.kodi/addons ... so it will be immediatelly used by your KODI (start the KODI from cli)
- Install Kodi XBMC module stubs: https://github.com/dwrobel/Kodistubs
- Open the plugin sources in Pycharm and set the proper interpreter (system interpreter what is python 2.7)
- Need to import libraries from:
	- ~/.kodi/addons/script.module.stream.resolver/lib
	- ~/.kodi/addons/script.module.stream.resolver/lib/contentprovider
	- ~/.kodi/addons/script.module.demjson/lib/demjson
	- ~/.kodi/addons/script.module.beautifulsoup4/lib
	- In PyCharm: File -> Settings -> Project -> Project Interpreter -> (Settings button) -> Show All -> (Show alll... button)
- Now you can run tv-lux-plugin-test.py and use pdb
- Check logs (if --debug enabled) in: ~/.kodi/temp/kodi.log