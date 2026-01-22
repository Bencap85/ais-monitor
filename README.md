# AIS Monitor
**AIS Monitor** is a real-time, global-scale AIS ingestion and vessel-tracking platform, built with distributed microservices, geospatial indexes, and real-time Websocket streaming.

![Image](https://github.com/user-attachments/assets/60ccaf51-c866-4a7a-85ee-016c5ed2737d)

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
![Image](https://github.com/user-attachments/assets/b01583f3-9aad-4db1-9071-799152f83627)
![Image](https://github.com/user-attachments/assets/82c7766a-325c-4061-8b14-a2e4904b64e4)
![Image](https://github.com/user-attachments/assets/68366387-6e6f-453d-9bb3-70c1d38bc62c)

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

