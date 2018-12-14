<h1 align="center">
  <img src="https://raw.githubusercontent.com/Data-Monkey/data-monkey.github.io/master/images/datamonkey.png" alt="DataMonkey Smart Home" width="200"> <br>
  Smart Home Configuration
</h1>

This repo serves mostly as my backup of the configuration I use in my home-assistant setup.<br>
How I installed it is described in this other repo over here: (https://github.com/Data-Monkey/HomeAutomation)

But I am happy for this repo to be inspirational for other Home Automation enthusiasts and if you can find some usefull code here, feel free to adapt it to your needs. Most likely I found it in somebody elses repo anyway :-)

The new file structure has been heavily influenced by [Frenck](https://github.com/frenck/) and his [HA Config structure](https://github.com/frenck/home-assistant-config). While this readme is influenced by [CCOSTAN](https://github.com/CCOSTAN) and the [Bear Stone Smart Home](https://github.com/CCOSTAN/Home-AssistantConfig). 

Please make sure you **star** this repo to keep up to date with the progress.
<div align="center">
  <h4>
    <a href="https://github.com/Data-Monkey/Home-Assistant-Config/stargazers"><img src="https://img.shields.io/github/stars/Data-Monkey/Home-Assistant-Config.svg?style=plasticr"/></a>
    <a href="https://github.com/Data-Monkey/Home-Assistant-Config/commits/master"><img src="https://img.shields.io/github/last-commit/Data-Monkey/Home-Assistant-Config.svg?style=plasticr"/></a>
  </h4>
</div>
<div align="center" font-color=orange><a name="menu"></a>
  <h4>
    <a href="https://github.com/Data-Monkey/Home-Assistant-Config#why">
      Why?
    </a>
    <span> | </span>
    <a href="https://github.com/Data-Monkey/Home-Assistant-Config#how">
      How?
    </a>
    <span> | </span>
    <a href="https://github.com/Data-Monkey/Home-Assistant-Config#software">
      Software
    </a>    
    <span> | </span>
    <a href="https://github.com/Data-Monkey/Home-Assistant-Config#hardware">
      Hardware / Gadgets
    </a>    
    <span> | </span>
    <a href="https://github.com/Data-Monkey/Home-Assistant-Config/issues">
      ToDo List
    </a>
    <span> | </span>
    <a href="https://github.com/Data-Monkey/Home-Assistant-Config/tree/master/config">
      Code
    </a>
  </h4>
</div>

<h2>Why?</h2>
Really, the question should be <b>"Why NOT?!"</b> <br>
Why wouldn't you want to automate your home? 
But then, what is home automation? I didn't want to replace a light bulb with a smart light and as a result I now have to find my phone, open the app and change the status every time I want to switch on/off my light.<br>
Home-Automation needs to make life easier!<br>
So I was looking for tasks that I can actually automate. 
Thinking back now, one of my earliest home-automation was to buy a harmony remote. One to rule them all :-) So now I don't need 2 or 3 remotes anymore, just to switch on the TV, change the input, switch on the DVR and browse to the recording or channel. 
Other simple automations that are now running in our appartment are looking after some lights. The ensuite light and wardrobe light are fully automated.
More challanging tasks are still in the making. Don't let the TV be switched on until todays chores (homework mostly) are done!

<h2>How?</h2>
This is what you are here for, so lets just dive in!<br>
Home Assistant and most of the other software used for home automation are installed in docker containers on an <a href="https://unraid.net/">unRAID</a> server. The build of this server is discussed in the <a href="https://forums.lime-technology.com/topic/30331-first-unraid-build-h87i-plus-lian-li-pc-q25/">unRAID forum</a>. <br>
The unRAID server is called TOWER and is the backbone of most things happening in our appartment. It serves as Media Server via Plex as well as a backup for all our laptops and photo library. And it also hosts all the software required for our Home Automation.

<h2>Software</h2>
As mentioned the unRAID TOWER runs docker with the following containers relevant to home automation

<table align="center" border="0">
<tr>
  <td align="center" width=20%>
    <a href="https://home-assistant.io">
      <b>Home Assistant</b><br>
      <img src="https://raw.githubusercontent.com/balloob/unraid-docker-templates/master/balloob/home-assistant-icon.png" width=100>
    </a>
    <a href="https://registry.hub.docker.com/u/homeassistant/home-assistant/">dockerhub</a>
  </td>
  <td>
    Home Assistant is the software that holds everything together. It is an Open Source project supported by a great communityt and this REPO is all about how I configured my HA instance.
  </td>
  </tr><tr>
  <td align="center">
    <a href="http://mqtt.org/">
    <b>MQTT</b><br>
    <img src="http://i.imgur.com/Cc9Jkcr.png" width=100>
    </a>
    <a href="https://hub.docker.com/u/spants/mqtt/">dockerhub</a>    
  </td>
    <td>
      MQTT is a lightweight protocol that lets devices communicate with each other. 
      I use it to let my devices communicate with HA. <br>
      I am still trying to come up with a topic strucutre that makes sense and is supported by my devices. 
      See this post <a href="https://community.home-assistant.io/t/mqtt-topic-design/69687">MQTT Topic Design</a>
    </td>
  </tr><tr>  
  <td align="center">
    <a href="https://www.influxdata.com/time-series-platform/influxdb/">
      <b>InfluxDB</b><br>
      <img src="https://raw.githubusercontent.com/pootzko/InfluxData.Net/master/nuget-icon.png" width=100>
    </a>
    <a href="https://hub.docker.com/_/influxdb/">dockerhub</a>
  </td>
  <td>
    InfluxDB is where I store a time series of some of my HA <a href="https://github.com/Data-Monkey/Home-Assistant-Config/blob/master/config/packages/influxdb.yaml">entities</a>
  </td>
</tr><tr>
  <td align="center">
    <a href="http://www.grafana.org">
    <b>Grafana</b><br>
    <img src="https://github.com/atribe/unRAID-docker/raw/master/icons/grafana.png" width=100>
    </a>
    <a href="https://hub.docker.com/r/grafana/grafana/">dockerhub</a>
  </td>
    <td>
      Grafana is used to visualise the data stored in InfluxDB.
    </td>
  </tr><tr> 
  <td align="center">
    <a href="http://www.duckdns.org">
    <b>DuckDNS</b><br>
    <img src="https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/duckdns.png" width=100>
    </a>
    <a href="https://hub.docker.com/r/linuxserver/duckdns/">dockerhub</a>
  </td>
    <td>
      DuckDNS is a free Dynamic DNS address service. 
      I use it to find my home network from the outside. The public access is required for my Google Assistant integration.
    </td>
  </tr><tr> 
  <td align="center">
    <a href="https://letsencrypt.org/">
    <b>Let's Encrypt</b><br>
    <img src="https://raw.githubusercontent.com/linuxserver/docker-templates/master/linuxserver.io/img/letsencrypt.png" width=100>
    </a>
    <a href="https://hub.docker.com/r/linuxserver/letsencrypt/">dockerhub</a>
  </td>
    <td>
      The Let's Encrypt docker provides me with my certificates.<br>
      This specific docker also comes with it's internal Nginx webserver and reverse proxy.
    </td>
  </tr><tr>
</table>

<br>
not in use anymore:
<br>

- Zanzito on Nexus5 mobile (http://www.barbaro.it/cms/index.php/83-zanzito)

- GPS Logger on Nexus5  (might ditch that for the Zanzito implementation)

- wrote a little script to track Crashplan Backup progress

<h2>Hardware</h2>

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

- Google Home (x2) 

- RasPlex (not realy any integration)

- Google WiFI (no integration yet, but keeps all my IoT devices from accessing Internet as they are all paused in the family feature)

- Sonoff to autoamate bathroom exhaust fan

- Smart Lights (Yeelight linked to Xiaomi Body Sensors)

- PiVPN (currently not used, need to work out integration with Google WiFi)

<br>
Some of my hardware has been retired for various reasons:

- Roku2  (replaced with RasPlex as PLEX was not updated on ROKU)

