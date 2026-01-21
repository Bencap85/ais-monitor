# AIS Monitor
**AIS Monitor** is a real-time, global-scale AIS ingestion and vessel-tracking platform, built with distributed microservices, geospatial indexes, and real-time Websocket streaming.

<img src="[https://private-user-images.githubusercontent.com/93168579/538688871-2d40fb51-b017-4b37-bcb3-74783e2272be.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjkwMTk4NzksIm5iZiI6MTc2OTAxOTU3OSwicGF0aCI6Ii85MzE2ODU3OS81Mzg2ODg4NzEtMmQ0MGZiNTEtYjAxNy00YjM3LWJjYjMtNzQ3ODNlMjI3MmJlLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTIxVDE4MTkzOVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTBkZjRkYzJkMzJmODIwMGU3ZjZjOTFkMDBiNWMzOTg1YWFhNGE2NTM2MTU1MmY3MTEwN2M4MTQ1ZWEyYTdkNzYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.v_C5qf0wuIYLPJ23cS0US5tScDAbaLuzpRcMAiV98aI](https://private-user-images.githubusercontent.com/93168579/538688871-2d40fb51-b017-4b37-bcb3-74783e2272be.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjkwMzQ5NzksIm5iZiI6MTc2OTAzNDY3OSwicGF0aCI6Ii85MzE2ODU3OS81Mzg2ODg4NzEtMmQ0MGZiNTEtYjAxNy00YjM3LWJjYjMtNzQ3ODNlMjI3MmJlLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTIxVDIyMzExOVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWIyM2UwMWUwMTdkOWRkOGM1YWE0ODZmNDhlZDM0YzZiMmQ5YTM4MzljYTc3Nzc4ZjViZTYwZjc2YzZmZjFlNTYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.zUtceUe5KRcNCUFYsVoEzP-QwJVQf84_bLcmd1v6VnU)">


## Overview
**AIS Monitor** is a full-stack Automatic Identification System (AIS) monitoring platform, enabling the real-time tracking of thousands of vessels worldwide. The system ingests live AIS messages, processes them through a distributed event‑driven backend, stores geospatial data in PostGIS, and streams updates to an interactive map‑based UI.

Users can:

  - View live vessel positions
  - Search and filter ships by MMSI, name, type, and other attributes
  - Inspect detailed vessel metadata
  - Examine historical vessel movements
  - Monitor large geographic regions with high‑throughput, low‑latency updates


## System Architecture
**AIS Monitor** is composed of several components:

### Backend
Event‑driven microservices written in Python
  - SNS topics and SQS queues for asynchronous communication
  - Docker‑based services for consistent development and deployment
  - CI/CD pipelines that automatically build and deploy services
  - Terraform‑managed AWS infrastructure for reproducibility and version control

### Frontend
React application with Redux for global state management
  - Map visualization built with react‑leaflet
  - Low-latency WebSocket streaming for continuous position updates
  - Highly-responsive search and filtering tools for vessel analysis
  - Viewport‑aware fetching algorithm that retrieves only relevant ships

### Database
PostgreSQL database featuring:
  - PostGIS for geospatial indexing and spatial queries
  - TimescaleDB for managing large-scale temporal data

## Media
<img src="https://private-user-images.githubusercontent.com/93168579/538715300-8d5342cd-a684-455f-ae3d-593a43a6f683.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjkwMTk5ODIsIm5iZiI6MTc2OTAxOTY4MiwicGF0aCI6Ii85MzE2ODU3OS81Mzg3MTUzMDAtOGQ1MzQyY2QtYTY4NC00NTVmLWFlM2QtNTkzYTQzYTZmNjgzLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTIxVDE4MjEyMlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTAwZjE0YTVlOThjMjgwMTFmNmU4NTQ5ODAwNTJlMjdhZGNjNDg1YTJhYjY4MjI4NjU4ZGYwMjM1OWQ0OGU5M2EmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.qMeXphRLgGV9zwBK24pIXxokkXcoAKQ7VoHus-XNHuU">

<img src="https://private-user-images.githubusercontent.com/93168579/538715259-c064c4a6-8499-42b1-8cc1-81bfa94eeec4.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjkwMjAxMDcsIm5iZiI6MTc2OTAxOTgwNywicGF0aCI6Ii85MzE2ODU3OS81Mzg3MTUyNTktYzA2NGM0YTYtODQ5OS00MmIxLThjYzEtODFiZmE5NGVlZWM0LmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTIxVDE4MjMyN1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTU0ZTE1YjAzZGIwZDIzNGFmOGRhZjlmZTdjNTgwYjllYmU3ODhjNGI2MTY0Mjg4NTgwZWYxODgxY2NhZjE3MWYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.V8jR7NRiawlWpm9Ba-MlDV3eRW7f8mDCMLQw9q2kQMU">

<img src="https://private-user-images.githubusercontent.com/93168579/538715208-8275ead2-a216-4f7c-a06c-36cc3c81840f.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjkwMTk5ODIsIm5iZiI6MTc2OTAxOTY4MiwicGF0aCI6Ii85MzE2ODU3OS81Mzg3MTUyMDgtODI3NWVhZDItYTIxNi00ZjdjLWEwNmMtMzZjYzNjODE4NDBmLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjAxMjElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwMTIxVDE4MjEyMlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTRjMWJmMmE4YTQyMTI2ZTM0ZmEyMzU2NDhjYWU3ZWY3N2JiNTE5NWFmZmU0NjI1YWYxZjU0OWY1ZTA1MzNjOGEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.5OzW9-ZwdA6KwbJ_ZUxtt1nYqcuNunnNudaohrH1R_k">

## Technical Challenges / Solutions

### High-Throughput Database Writes
AIS messages arrived at high frequency, overwhelming the database with write requests.

**Solution:** Batch inserts and deduplicate requests before writing to PostGIS, enabling the repository service to keep pace with ingestion.

### Observability and Back Pressure Monitoring
When designing distributed systems, observability and monitoring are essential to ensuring system health. 

**Solution:** Each microservice exposes a metrics endpoint, aggregated into a simple dashboard for continous monitoring of throughput, latency, etc.

### Efficient Live Data Streaming
Broadcasting every update to every client would overwhelm both the server and the browser. 

**Solution:** Partition the world into WebSocket "rooms." Clients subscribe only to relevant rooms, dramatically reducing load.

### Database Query Performance
Repeated client requests triggered overlapping queries that overwhelmed the database.

**Solution:** A query manager tracks inflight requests per client and cancels out-dated queries, ensuring only the most up-to-date queries are executed, greatly improving query performance and reducing database load. 

### Sustained Data-Intensive Throughput
Ingesting and processing 12GB/day gradually eroded the PostGIS's ability to keep up with write requests and prevented it from running autovacuum, resulting in a death spiral of overlapping, long-running checkpoints. 

**Solution:** Vertically-scaling the hardware inside AWS EC2 instance provided PostGIS with the processing power needed to sustain the system's throughput. 

### Storing Worldwide Temporal Data
Storing this large-scale temporal data resulted in the database growing by millions of records a day. This scale impacted query performance and increased the space required by the indexes.

**Solution:** 
Partitioning the database by time massively reduced table size, minimized index bloat, and improved the performance of time-based queries by grouping data by time. The PostgreSQL extension TimescaleDB was used to handle this partitioning.

