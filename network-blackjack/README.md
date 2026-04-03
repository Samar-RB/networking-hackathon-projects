# Network Blackjack (Client-Server)

## Overview
This project implements a client-server Blackjack game in Python.

The server hosts the game, manages the deck and game logic, and communicates with clients over the network. Clients discover available servers using UDP broadcast and play multiple Blackjack rounds over TCP.

## Features
- Client-server architecture
- UDP broadcast for server discovery
- TCP communication for game sessions
- Multi-round Blackjack gameplay
- Round results and win-rate statistics
- Custom packet formats for offers, requests, and payloads

## Technologies
- Python
- Socket Programming
- TCP / UDP protocols
- Client-Server Systems

## How It Works
- The server broadcasts offer messages via UDP
- Clients listen for available servers
- Clients connect to the server over TCP
- The game is played for the requested number of rounds
- The client prints results and final win statistics

## Key Concepts
- Network protocol design
- Client-server communication
- Game state management
- Packet encoding and decoding
- Error handling and compatibility

## Skills Demonstrated
- Network programming in Python
- Designing interoperable protocols
- Implementing multiplayer-style game logic
- Handling sockets, packets, and communication flow
