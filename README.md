# AIS Monitor
**AIS Monitor** is a real-time, global-scale AIS ingestion and vessel-tracking platform, built with distributed microservices, geospatial indexes, and real-time Websocket streaming.

![Image](https://github.com/user-attachments/assets/60ccaf51-c866-4a7a-85ee-016c5ed2737d)

## Overview
Automatic Identification System (AIS) data is foundational for maritime domain awareness, anomaly detection, logistics, and national security. This system demonstrates the ability to ingest, process, and analyze global maritime traffic in real time.

**AIS Monitor** is a full-stack AIS monitoring platform, enabling the real-time tracking of thousands of vessels worldwide. The system ingests live AIS messages, processes them through a distributed event‑driven backend, stores geospatial data in PostGIS, and streams updates to an interactive map‑based UI.

Users can:

  - View live vessel positions
  - Search and filter ships by MMSI, name, type, and other attributes
  - Inspect detailed vessel metadata
  - Examine historical vessel movements
  - Monitor large geographic regions with high‑throughput, low‑latency updates


## System Architecture

### Backend
Event‑driven microservices written in Python
  - SNS topics and SQS queues for asynchronous communication
  - Docker‑based services for consistent development and deployment
  - CI/CD pipelines using GitHub Actions that automatically build and deploy services
  - Terraform‑managed AWS infrastructure for reproducibility and version control

### Frontend
React application with Redux for global state management
  - Map visualization built with react‑leaflet
  - Low-latency WebSocket streaming for continuous position updates
  - Highly-responsive search and filtering tools for vessel analysis
  - Viewport‑aware fetching algorithm that retrieves relevant ships and dynamically subscribes to relevant WebSocket channels

### Database
PostgreSQL database featuring:
  - PostGIS for geospatial indexing and spatial queries
  - TimescaleDB for managing large-scale temporal data

## System Metrics
   - **Daily ingestion volume:** ~12 GB (≈19 million AIS messages)
   - **Average throughput:** ~200-225 messages/sec
   - **End‑to‑end latency:** < 200ms
   - **Active dataset:** 7‑day rolling window

## Demos
![Image](https://github.com/user-attachments/assets/b01583f3-9aad-4db1-9071-799152f83627)
![Image](https://github.com/user-attachments/assets/82c7766a-325c-4061-8b14-a2e4904b64e4)
![Image](https://github.com/user-attachments/assets/68366387-6e6f-453d-9bb3-70c1d38bc62c)


## Technical Challenges / Solutions

### High-Throughput Database Writes
AIS messages arrived at high frequency, overwhelming the repository service with write requests. This write bottleneck caused growing queue backpressure, dropped messages, and eventually service crashes.

**Solution:** Perform batch inserts and deduplicate requests before writing to PostGIS, enabling the repository service to keep pace with ingestion and minimize queue backpressure.

### Observability and Back Pressure Monitoring
When designing distributed systems, observability and monitoring are essential to ensuring system health, detecting anomalies, and diagnosing errors. 

**Solution:** Each microservice exposes a metrics endpoint, aggregated into a simple dashboard for continous monitoring of throughput, latency, etc.

### Efficient Live Data Streaming
Broadcasting every global position update to every active client would inundate the client with irrelevant messages and require the server to perform redundant fan-out work for data clients do not care about.

**Solution:** Partition the world into WebSocket channels correposponding to geographic locations (e.g., by map tile). Clients subscribe only to relevant channels, reducing server-side fan-out, minimizing network traffic, and ensuring clients only receive updates relevant to their visible viewport

### Database Query Performance
Repeated client requests triggered overlapping queries that overwhelmed the database.

**Solution:** A custom QueryManager class tracks inflight requests per client and cancels out-dated queries, ensuring only the most up-to-date queries are executed, greatly improving query performance and reducing database load. 

### Sustained Data-Intensive Throughput
Ingesting and processing 12GB/day gradually eroded Postgres' ability to keep up with write requests and prevented it from running autovacuum, resulting in a death spiral of overlapping, long-running checkpoints. 

**Solution:** Vertically-scaling the hardware inside AWS EC2 instance provided PostGIS with the processing power needed to sustain the system's throughput. 

### Storing Worldwide Temporal Data
Storing this large-scale temporal data resulted in the database growing by millions of records a day. This scale impacted query performance and increased the space required by the indexes.

**Solution:** 
Partitioning the database by time massively reduced table size, minimized index bloat, and improved the performance of time-based queries by grouping data by time. The PostgreSQL extension TimescaleDB was used to handle this partitioning and maintain a 7-day rolling window of data.

## Getting Started
This project includes:
  - a containerized AWS‑native backend (running against LocalStack)
  - a React UI
  - Terraform‑managed AWS resources (SNS/SQS)

Local development uses Docker Compose and LocalStack to simulate AWS services.

1. Install prerequisites
    
    You will need:
    - Docker + Docker Compose
    - Terraform (v1.5+ recommended)
    - Node.js  (v18+ recommended)

2. Clone the repository
    ```
    git clone https://github.com/Bencap85/ais-monitor.git
    cd ais-monitor
    ```

3. Set up backend environment variables
    ```
    cd api
    cp .env.example .env
    ```
    Only one value must be updated:
    `WS_API_KEY=your_AISStream_API_key`
    All other values can remain as provided.

4. Start and build LocalStack infrastructure
    
    Run this command to start LocalStack: `docker compose --profile infra up --build -d`

5. Provision (LocalStack) AWS resources with Terraform

    ```
    cd terraform/dev
    terraform init
    terraform apply -auto-approve
    ```

    Note: The command `terraform output` will print the LocalStack endpoints. The configuration provided in the .env.example should be correct, but the values can be confirmed here.

6. Start backend services

    Return to api directory:
    ```
    cd ../..
    ```
    And run:
    ```
    docker compose --profile dev up --build -d
    ```
    This starts:
      - Ingestor service
      - Repository service
      - Broadcaster service
      - PostgreSQL database with PostGIS and TimescaleDB

7. Set up and start the UI

    ```
    cd ../ui/app
    cp .env.example .env
    ```

    A free example tile server is provided in the .env.example. If you wish, a different provider can be specified by updating:
    ```
    REACT_APP_TILE_SERVER_URL=
    REACT_APP_TILE_SERVER_ATTRIBUTION=
    ```

    Then start the UI:
    ```
    npm install
    npm start
    ```
    The UI will be available at:
    `http://localhost:3000`