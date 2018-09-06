# Home Assistant Configuration

this repo serves as my backup of the configuration I use in my home-assistant.io setup.
How I installed it is described in the other repo.
(https://github.com/Data-Monkey/HomeAutomation)

I will try to list the components that I use in this file and please feel free to ask me questions.

<h1>Components</h1>


<h2> Hardware </h2>

- HA is installed in a docker hosted on an unRAID box

- Xiaomi Gateway (x2)             [shop](https://www.gearbest.com/living-appliances/pp_344667.html?wid=21)
  with a few
  - Temperature Sensors           [shop](https://www.gearbest.com/living-appliances/pp_344665.html?wid=21)
  - Body Sensors                  [shop](https://www.gearbest.com/smart-light-bulb/pp_257678.html?wid=21)
  - Door Sensors                  [shop](https://www.gearbest.com/smart-light-bulb/pp_257677.html?wid=21)
  - Power Plugs                   [shop](https://www.gearbest.com/living-appliances/pp_344666.html)
  - Buttons                       [shop](https://www.gearbest.com/smart-light-bulb/pp_257679.html)
  - Water Sensor                  [shop](https://www.gearbest.com/home-smart-improvements/pp_668897.html)

- Logitech Harmony Hub (not integrated yet)

- Sonos Playbar + Sub

- Chromecast + Audio Cast

- Efergy Energy Monitor           (demo: https://engage.efergy.com/dashboard)

- Roku2  (replaced with RasPlex as PLEX was not updated on ROKU)

- Google Home (x2) 

- RasPlex (not realy any integration)

- Google WiFI (no integration yet, but keeps all my IoT devices from accessing Internet as they are all paused in the family feature)

- Sonoff to autoamate bathroom exhaust fan

- Smart Lights (Yeelight linked to Xiaomi Body Sensors)

- PiVPN (currently not used, need to work out integration with Google WiFi)

<h2> Software </h2>

- Dockers on unRAID (https://forums.lime-technology.com/topic/30331-first-unraid-build-h87i-plus-lian-li-pc-q25/)
  - influxdb 
  - grafana
  - mqtt
  - lets-encrypt

- Zanzito on Nexus5 mobile (http://www.barbaro.it/cms/index.php/83-zanzito)

- GPS Logger on Nexus5  (might ditch that for the Zanzito implementation)

- wrote a little script to track Crashplan Backup progress


