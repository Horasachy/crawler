# Buc-crawler
This project contains crawlers and collected datasets for D2B projects.

## How to use this Docker image

```
docker login registry.gitlab.com
docker run -p 5000:5000 -p 6800:6800 registry.gitlab.com/inside-solutions/buc-crawler
```
or:
```
docker build -t crawler . 
docker run -p 5000:5000 -p 6800:6800 crawler:latest 
```

ScrapydWeb Server
http://localhost:5000

Scrapyd Server
http://localhost:6800

## How to run spiders
Go to: 
```
http://localhost:5000
```
Select on the left in the menu: 
```
Operations -> Deploy Project
```
```
Click: Package & Deploy
```
```
Select: spider
```
```
Click: Check CMD & Run Spider
```