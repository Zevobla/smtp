# Stripe Market Tool Project

This project realize very basic market logic

## How to Run the Project

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Zevobla/smtp
   cd smtp
   ```

2. **Set Up Environment Variables**:
   Copy the `example.env` file to `.env` and update the values as needed.
   ```bash
   cp example.env .env
   ```

3. **Start the Docker Containers**:
   Ensure Docker is installed and running on your system. Then, start the containers:
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**:
   The application should now be running. Access it at `http://localhost:<port>` (replace `<port>` with the appropriate port number defined in your `docker-compose.yml`).

5. **Stop the Containers**:
   To stop the running containers:
   ```bash
   docker-compose down
   ```
