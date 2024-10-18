# **Timely Transport System**

---

## **1) Code**

This project is built using **FastAPI** for the backend (microservice architecture) and **HTML, CSS, JavaScript** for the frontend.

- **GitHub Project:**  
  *(GitHub project uploaded – please refer to the provided link)*

---

## **2) Documentation**

1. **High-Level Diagram (HLD):**  
   ![HLD Image](https://drive.google.com/uc?id=1IOWm93JPsc5wCR8B1oyaYY6zvy0PYDUH)
   
2. **Entity-Relationship Diagram (ERD):**  
   ![ERD Image](https://drive.google.com/uc?id=1Vxbk7QQJraOQ4DjzTrlbtlHEa_l13H20)

3. **Explanation Document:**  
   [View Explanation Document](https://drive.google.com/file/d/1dmTW8Bi0f2UegjHM_-ZgRUbZ93j1KhJm/view?usp=drive_link)

4. **Frontend Flow:**
   ![View FE Flow Image](https://drive.google.com/uc?1KeBdVbr5vQH0pd0z_glBiKmCr2XDMV0k)

5. **Documentation Folder**
    [View Folder](https://drive.google.com/drive/folders/1dX_RyZfF0mF4qX2hsZ2DJNcvfEDQ45rr?usp=drive_link)

6. **Video + App:**  
   - **Note:** Due to **Amazon billing issues**, the video demonstration will be delayed until this weekend, as some backend services could not be executed and deployment on **Amazon ECS** wasn’t possible either due to the same.  
   - **Try Locally:** If you wish to explore the system, follow the **Local Deployment steps** below to deploy the app on your local machine.

---

## **3) Local Deployment Instructions**

To run the project on your local machine:

### **Prerequisites:**
- **Docker** should be installed and running on your system.

### **Steps:**

1. **Clone the Repository:**
   ```bash
   git clone <GitHub Repository URL>
   cd <Project Directory>
   ```

2. **Update Environment Variables:**
   - Open the `.env` files for each service and **replace the values** that are marked as `" "`.

3. **Build and Run the Services Using Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Stop and Clean Docker Containers:**
   ```bash
   docker-compose down
   ```

5. **Access the Frontend:**
   - Navigate to the `frontend` folder and **open `index.js` in your browser**.

You are now ready to explore the **Timely Transport System**!

---

## **4) Some Major Points (Design Documentation)**


The **Timely Transport System** supports real-time ride-hailing with key features such as customer ride requests, driver tracking, and payment processing. The system leverages a **microservices architecture** to ensure scalability and performance.

### **1. System Functioning Overview**

The architecture supports a ride-hailing platform involving interactions between multiple actors: **customers, drivers, and administrators**. Below is an **end-to-end description of the flow**:

#### **Authentication Service:**
- Both customers and drivers must **register and log in** using this service.  
- It ensures that only authenticated users can access the system.

#### **Ride Request Handling:**
- Once authenticated, a **customer initiates a ride request**.  
- The **Driver Finding & Matching Service** processes the request by **finding nearby drivers in real-time**.

#### **Driver Matching and Notification:**
- The system uses the **Location Service** to **fetch nearby drivers** (leveraging **Redis** for fast reads).  
- If a driver is found, a notification is sent through the **Notification Service** (via **queues** for asynchronous communication).  
- Drivers can **accept or reject** the ride through the driver interface.

#### **Ride Creation and Status Updates:**
- Upon acceptance, the ride is created and tracked through the **Transport Management & Payment Service**.  
- **Ride statuses** (start/end) and **location updates** are captured via the **Location Service**.

#### **Real-time Location Tracking:**
- The **Location Service** uses **Redis** for real-time location updates (via **WebSocket** for low-latency communication).  
- Updates are streamed to the customer for **tracking during the ride**.

#### **Administration:**
- **Admin users** have access to **system monitoring** and can control various parameters via the **Administration Service**.

---

### **2. Key Design Decisions and Trade-offs**

#### **Use of Redis for Distributed Caching and Locking:**
- **Why Redis:** Redis is chosen for its **speed** and ability to handle **high throughput**.
- **Location Tracking:** Real-time location data is written to Redis to ensure **fast reads**.
- **Distributed Locking:** A **distributed lock mechanism** (using Redis) ensures that the same driver is not **double-booked** by parallel processes.

**Trade-off:**  
- Redis introduces **eventual consistency** since location updates may take a few milliseconds to propagate.  
- This is acceptable for location tracking, where the focus is on **latency over consistency**.

#### **Event-driven Communication Using Queues:**
- The architecture makes heavy use of **queues (asynchronous messaging)** for tasks like:
  - **Driver notifications**
  - **Ride creation and updates**

**Trade-off:**  
- Some operations may experience **slight delays** (e.g., a few milliseconds) due to message queuing.  
- However, this ensures **high availability** under heavy traffic.

#### **Stateless Microservices Architecture:**
- All services (e.g., **Driver Matching, Authentication**) are designed to be **stateless**, ensuring **easy horizontal scaling**.
- **Stateful data** (such as rides and payments) is handled by **databases and Redis**, ensuring **smooth recovery** in case of service restarts.

---

### **3. Handling High-volume Traffic and Scalability**

#### **API Gateway and Load Balancer:**
- The **API Gateway & Load Balancer** distribute incoming traffic evenly across multiple instances of microservices.
- The **load balancer** ensures **high availability** and helps the system handle **spikes in traffic** efficiently.

#### **Horizontally Scalable Microservices:**
- Each service is deployed **independently** and can **scale horizontally** by adding more instances during peak times (e.g., Driver Matching and Location Services).

#### **Optimized Real-time Location Tracking with WebSocket:**
- A **WebSocket-based location update mechanism** ensures **low-latency streaming** of location updates, critical for **customer tracking and driver routing**.

#### **Partitioning with Redis and Databases:**
- **Redis sharding/partitioning** is used to distribute the load of real-time location updates and caching across multiple Redis nodes.
- **Database replication and partitioning** ensure that **transactional data** (such as rides and payments) is available even during high traffic.

---

### **4. Distributed Data Handling and Load Balancing**

#### **Distributed Locking (Redis):**
- The **Distributed Lock** ensures that the **same driver isn’t assigned multiple rides** by concurrent ride-matching processes.

#### **Asynchronous Queues:**
- **Queues offload operations** that don’t need immediate processing (e.g., notifications), improving throughput.

#### **WebSocket-based Location Service:**
- By maintaining a **long-lived WebSocket connection**, the **Location Service** minimizes the overhead of repeated HTTP requests, ensuring better performance for **real-time tracking**.

#### **Database and Redis Integration:**
- **Redis caches frequently accessed data** (like driver statuses and locations).
- The **main DB** stores **transactional data** (e.g., ride details, payments) with **backup and replication strategies** to avoid data loss.

---

### **5. Performance and Scalability Summary**

- **Stateless microservices** and **horizontal scaling** allow each component to handle increased load independently.
- **Redis-based caching** accelerates real-time operations like location tracking and driver status management.
- **Queues and asynchronous messaging** ensure **non-blocking, high-performance communication** between services.
- **WebSocket-based location tracking** reduces latency for **real-time ride tracking**, enhancing the user experience.
- **API Gateway & Load Balancer** distribute incoming traffic to **prevent overload** on individual services.

This architecture ensures **high availability, low latency, and fault tolerance**, making it suitable for handling the demands of a **large-scale ride-hailing platform**.

---

Thank you for using the **Timely Transport System**!