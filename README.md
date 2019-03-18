# akoteka

The aim of this project is to produce a software which helps to organize and play media

<table border="0">
<tr>  
<td><img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/cardlist-simple.png' width='400'>
<td><img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/cardlist-filter.png' width='400'> 
<td><img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/cardlist-setting.png' width='400'> 
<tr/>
<tr>
<td>Normal view<br>
<td>Filter<br>
<td>Setting<br> 
<tr/>
<table>



## The main features are:
- Navigation in the Card hierarchy
  - <img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/card-navigation.png' width='600'>    

- Cards show the characteristics of the media
  - Title, Year, Length, Country, Sound, Subtitle, Director, Actor, Genre, Theme, Story
  - <img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/card-single.png' width='600'>    
- Indicate personal opinion about the media 
  - Favorite, Best, New
  - <img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/personalopinion.png' width='20'>   
- Paging Cards in card-holder
  - <img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/paging.gif' width='600'>

- Fast filtering Cards by title, genre, theme, director, actor ...
  - <img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/filter-fast.gif' width='600'>
  
- Advanced filtering Cards by title, genre, theme, language, director, actor, year ...
  - <img src='https://github.com/dallaszkorben/akoteka/blob/master/wiki/filter-advanced.gif' width='600'>

- Playing media one-by-one
- Continously playing media

## Usage

### Preconditions
 - Minimum Python3.6 should be installed on your computer
 - pip (compatible to the Python version) should be installed on your computer
 - The media collection should be already mounted on your file system

### Install

1. Run a console
2. On the console type the following  

		pip install akoteka

### Update

1. Run a console
2. On the console type the following  

		pip install akoteka --upgrade
		

### Run
1. Run a console
2. On the console type the following 

		akoteka
	
## Media

### Card folder

The application needs a special hierarchy of files to recognize media. A folder, which represents a Card, contains the 
- specific media file (**avi, mkv, mp4, mp3 ...**) 
- a descriptor file (**card.ini**) 
- optionaly an image (**image.jpg**).

### Container folder

Card Folders can contain many subfolders, which can themselves be a Card folder. In that case the folder should not contain any media file.



### card.ini file

The **card.ini** file is a simple text file containing key-value pairs which describe the media. Here is an example:
```console
[titles]
title_en=The Great Global Warming Swindle
title_hu=A nagy globális felmelegedés átverés

[storyline]
storyline_en=Everything you've ever been told about Global Warming is probably untrue. This film blows the whistle on the biggest swindle in modern history. We are told that 'Man Made Global Warming' is the biggest ever threat to mankind. There is no room for scientific doubt. Well, watch this film and make up your own mind.
storyline_hu=

[general]
year=2007
director=Martin Durkin
actor=Tim Ball,Nir Shaviv,Ian Clark,Piers Corbyn,
length=1:14
sound=en
sub=hu
genre=documentary
theme=lie,money,greed,conspiracy,stupidity
country=gb

[rating]
best=y
new=y
favorite=y

[links]
imdb=https://www.imdb.com/title/tt1020027/?ref_=nv_sr_1
```

### Card hierarchy
```console
.
├── -Aaron.Russo
│   ├── America.Freedom.To.Facism-2006
│   │   ├── America.Freedom.To.Fascism.avi
│   │   ├── America.Freedom.To.Fascism.sub
│   │   ├── card.ini
│   │   └── image.jpeg
│   ├── card.ini
│   ├── image.jpeg
│   ├── Interview.With.Aaron.Russo-2009
│   │   ├── card.ini
│   │   ├── image.jpeg
│   │   └── Interview.With.Aaron.Russo.avi
│   └── Mad.As.Hell-1996
│       ├── card.ini
│       ├── image.jpeg
│       └── Mad.As.Hell.divx
├── card.ini
├── Home-2009
│   ├── card.ini
│   ├── Home.mkv
│   └── image.jpeg
├── image.jpeg
├── Inside.Job-2010
│   ├── card.ini
│   ├── image.jpeg
│   └── Inside.Job.mkv
├── -Michael.Moore
│   ├── Bowling.For.Columbine
│   │   ├── Bowling.For.Columbine-2002.mkv
│   │   ├── card.ini
│   │   └── image.jpeg
│   ├── card.ini
│   ├── Fahrenheit911-2004
│   │   ├── card.ini
│   │   ├── Fahrenheit.911.mkv
│   │   └── image.jpeg
│   └── image.jpeg
├── The.Age.Of.Stupid-2009
│   ├── card.ini
│   ├── image.jpeg
│   └── The.Age.Of.Stupid.mkv
├── The.Corporation-2003
│   ├── card.ini
│   ├── image.jpeg
│   └── The.Corporation.mkv
├── The.Great.Global.Warming.Swindle-2007
│   ├── card.ini
│   ├── image.jpeg
│   ├── TheGreatGlobalWarmingSwindle.avi
│   └── TheGreatGlobalWarmingSwindle.srt
├── The.Light.Bulb.Cosnpiracy
│   ├── card.ini
│   ├── image.jpeg
│   └── The.Light.Bulb.Conspiracy.mp4
└── Who.Killed.The.Electric.Car-2006
    ├── card.ini
    ├── image.jpeg
    └── Who.Killed.The.Electric.Car.mkv
```
 



