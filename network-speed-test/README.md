# Network Speed Test (Client-Server)

## Overview
This project implements a client-server application that measures network performance using both TCP and UDP protocols.

The system allows multiple clients to connect to servers, request data transfers, and compare speed, latency, and packet loss.

## Features
- Multi-threaded client and server
- TCP data transfer
- UDP data transfer with packet tracking
- Real-time performance measurement
- Speed and packet loss statistics

## Technologies
- Python
- Socket Programming
- TCP / UDP protocols
- Multithreading

## How It Works
- The server broadcasts "offer" messages using UDP
- Clients listen for available servers
- Clients connect using TCP and UDP
- Data is transferred and measured
- Results include transfer speed and packet loss

## Key Concepts
- Client-Server architecture
- Network protocols (TCP vs UDP)
- Concurrency (threads)
- Performance measurement

## Skills Demonstrated
- Network programming in Python
- Handling multiple connections
- Protocol design and packet structure
- Error handling and robustness
