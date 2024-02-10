# HTTP/2 Rapid Reset Validator

### DISCLAIMER: This script is created to perform security validation on a zero-day vulnerability, intended to help security professionals to better understand the security posture of their web assets. ANY usage in a malicious manner and the repercussions that comes with it is outside of my responsibility. Use it wisely.

## Description

This custom script is created to perform Security Validation of the HTTP/2 Rapid Reset (CVE-2023-44487) vulnerability on a web server, in a non-intrusive manner. The base logic of this script consists of it sending a single RST_STREAM after trying to establish a TCP channel, and checking to determine whether the vulnerability is present or not.

## About CVE-2023-44487

CVE-2023-44487, otherwise known as "HTTP/2 Rapid Reset", is a zero-day vulnerability that allows threat actors to perform DDoS by manipulating the Rapid Reset stream (RST_STREAM) within the multiplexing characteristics of HTTP/2. Multiplexing is a technique used by HTTP/2 to allow multiple simultaneous communications to be performed in a single TCP connection/channel (see figure below), instead of creating different dedicated channels for each exchange, as used in previous HTTP/1.1 version.

![HTTP/2 Multiplexing]()

With the multiplexing technique in place, HTTP/2 also employs a method to optimize channel usage, with a method of canceling (or entirely halts) the request using RESET FRAMES, dubbed the "RST_STREAM" frame. This is where the vulnerability is present. Threat actors have found a way to send RST_STREAM directly after the original requests, in an extremely large amount and rapid manner, and in a way that the requests eventually exceeds the keepalive limit for concurrent streams (see figure below). This would result the server utilizing HTTP/2 to become overwhelmed, rendering it useless, thus a successful DDoS attack is performed.

![RST_STREAM VULN]()

## Key Features
This script contains the following key features: 
* Function to check if the target web server is utilizing HTTP/2
* HTTP/2 / TCP Connection establishment attempt to the target web server
* RST_STREAM delivery attempt, right after the connection is made
* Determining if CVE-2023-44487 is present on the target.

## Installation
```sh
git clone https://github.com/ge-wijayanto/http2-rapid-reset-validator.git
```

## Usage Guide
```py
Open Terminal

## Run script
python http2-rapid-rst.py
```

## Result Sample
![Result Sample 1]()