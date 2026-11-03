#!/usr/bin/env python3
"""Deterministically merge the reviewed SHAPP backend map into its catalogs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'installer/catalog/shapp-apps.json'
STACK = ROOT / 'installer/catalog/shai-stack-services.json'
RECIPES = {
    'esphome': ('ghcr.io/esphome/esphome:stable', 6052, 6052, [('/config','config')]),
    'node-red': ('nodered/node-red:latest', 1880, 1880, [('/data','data')]),
    'openhab': ('openhab/openhab:latest', 18080, 8080, [('/openhab/conf','conf'),('/openhab/userdata','userdata'),('/openhab/addons','addons')]),
    'jellyfin': ('jellyfin/jellyfin:latest', 8096, 8096, [('/config','config'),('/cache','cache'),('/media','media')]),
    'plex': ('plexinc/pms-docker:latest', 32400, 32400, [('/config','config'),('/data','media'),('/transcode','transcode')]),
    'emby': ('emby/embyserver:latest', 8097, 8096, [('/config','config'),('/mnt/share','media')]),
    'navidrome': ('deluan/navidrome:latest', 4533, 4533, [('/data','data'),('/music','media')]),
    'zwavejs': ('ghcr.io/zwave-js/zwave-js-ui:11.25.2', 8091, 8091, [('/usr/src/app/store','store')]),
    'adguard-home': ('adguard/adguardhome:latest', 3001, 3000, [('/opt/adguardhome/work','work'),('/opt/adguardhome/conf','conf')]),
    'pi-hole': ('pihole/pihole:latest', 8082, 80, [('/etc/pihole','config')]),
    'matter-server': ('ghcr.io/matter-js/matterjs-server:stable', 5580, 5580, [('/data','data')]),
    'emoncms': ('openenergymonitor/emoncms:latest', 8099, 80, [('/var/opt/emoncms/phpfina','phpfina'),('/var/opt/emoncms/phptimeseries','phptimeseries')]),
}

def main():
    apps = json.loads(APP.read_text())
    stack = json.loads(STACK.read_text())
    apps['apps'] = [entry for entry in apps['apps'] if entry['id'] != 'xscreensaver']
    additions = [
        {'id':'luks-encryption','name':'Ubuntu LUKS Disk Encryption Tools','category':'optional','description':'Install cryptsetup for LUKS volumes. Ubuntu Disks provides the existing GUI. Installing tools does not encrypt, erase, reformat or repartition disks; encrypting an installed system requires a separate reviewed plan.','packages':['cryptsetup'],'disk_mb':30,'ram_mb':32,'network':'Ubuntu package download; offline encryption tools','available':True,'status':'Tools only; no disk changes are executed by SHAPP'},
        {'id':'veracrypt','name':'VeraCrypt for Ubuntu','category':'optional','description':'Official Ubuntu GUI package for encrypted containers and volumes. Publisher PGP signature verified before installation. No automatic encryption or disk changes.','packages':[],'disk_mb':100,'ram_mb':96,'network':'Official HTTPS package/key download; offline during use','available':False,'host_backend':'veracrypt','status':'Exact-release Ubuntu package with verified publisher signature'},
    ]
    for entry in additions:
        if not any(app['id'] == entry['id'] for app in apps['apps']):
            apps['apps'].append(entry)
    for app in apps['apps']:
        key = app['id']
        if key in {'piper', 'whisper', 'openwakeword', 'wyoming', 'esphome', 'sniffnet', 'zeek', 'ntopng', 'veracrypt'}:
            app['host_backend'] = key
            app['status'] = 'Visible-terminal host installer; runtime installation is separate from service/model configuration'
        if key in RECIPES:
            image, host, container, volumes = RECIPES[key]
            app['container_service'] = key
            app['status'] = 'Advanced Docker installer; loopback UI; persistent data; first-run app setup may be required'
            stack['services'][key] = {
                'name': app['name'], 'image': image,
                'minimum_ram_mb': app['ram_mb'], 'minimum_disk_mb': app['disk_mb'],
                'ports': [{'port': host, 'protocol': 'tcp', 'scope': 'loopback', 'purpose': app['name'] + ' local administration'}],
                'generic': {'container_port': container, 'mounts': [{'target': t, 'folder': f} for t,f in volumes],
                            'outbound': key == 'plex', 'uid': 1000 if key in {'node-red','navidrome'} else None},
            }
        if key in {'pi-hole','adguard-home'}:
            app['network'] = 'Online image download; local-only initial setup. Does not change host/router DNS or DHCP. Explicit network review required for LAN deployment.'
        if key == 'zwavejs':
            app['status'] += '; exactly one reviewed serial-by-id controller required'
        if key == 'speech-to-phrase':
            app['status'] = 'Needs language, Home Assistant training and voice model selection; not a generic pip install'
        if key == 'matter-server':
            app['status'] = 'Download/stage the current Matter.js runtime only; activation requires an explicitly reviewed IPv6/networking exception'
            stack['services'][key]['generic']['download_only'] = True
        if key == 'ntopng':
            app['status'] = 'Stable upstream Ubuntu repository with scoped verified key; capture daemon stays disabled pending configuration'
        if key == 'zeek':
            app['status'] = 'Official Ubuntu repository; scoped verified key and Zeek 9.0 LTS installation; no automatic capture'
        if key == 'emoncms':
            app['status'] = 'Advanced private web/database/Redis stack with generated credentials; optional MQTT configured separately'
            app['ram_mb'] = 1100
            stack['services'][key]['minimum_ram_mb'] = 1100
            stack['services'][key]['components'] = {'db': 'mariadb:11.8', 'redis': 'redis:8'}
    APP.write_text(json.dumps(apps, indent=2) + '\n')
    STACK.write_text(json.dumps(stack, indent=2) + '\n')

if __name__ == '__main__': main()
