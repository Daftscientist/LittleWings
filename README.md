# LittleWings

LittleWings is a web application designed to manage and interact with Docker containers via a WebSocket-based interface. This project leverages the Sanic web framework to handle HTTP and WebSocket requests, enabling real-time communication and control of Docker containers.

## Features

- **WebSocket Integration**: Real-time interaction with Docker containers through WebSocket.
- **Docker Log Streaming**: Stream Docker container logs to the client in real-time.
- **Command Execution**: Execute commands on Docker containers via WebSocket messages.
- **Heartbeat Mechanism**: Keep the WebSocket connection alive with a heartbeat system.
- **Protected Routes**: Secure WebSocket routes with authentication.
- **Server Management**: Includes server management scripts for various actions.

## Project Structure

```
/src
├── api
│   ├── websocket.py       # WebSocket handling and streaming
│   ├── manage.py          # Server management utilities
│   ├── server_action.py   # Actions to be performed on the server
│   └── server.py          # Server-related functionalities
├── core
│   ├── authentication.py  # Authentication mechanisms
│   ├── database.py        # Database initialization and closure
│   └── server.py          # Server class interacting with Docker
├── views
│   └── api_views.py       # API views registration
├── main.py                # Main entry point for the Sanic application
```

### Detailed File Description

- **api/websocket.py**: Handles WebSocket connections and streams Docker logs to the client.
- **api/manage.py**: Contains management utilities for server operations.
- **api/server_action.py**: Defines actions that can be performed on the server.
- **api/server.py**: Implements server functionalities, including Docker interactions.
- **core/authentication.py**: Contains authentication mechanisms, including the `protected_route` decorator.
- **core/database.py**: Manages database initialization and closure.
- **core/server.py**: The Server class interacts with Docker containers.
- **views/api_views.py**: Registers API views for HTTP routes.
- **main.py**: The main entry point for starting the Sanic application.

## Getting Started

### Prerequisites

- Python 3.8+
- Docker
- Sanic
- Other dependencies listed in `requirements.txt`

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Daftscientist/LittleWings.git
    cd LittleWings/src
    ```

2. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Ensure that your Docker environment is properly set up and that you have the necessary permissions to manage Docker containers.

### Running the Application

1. Start the Sanic application:

    ```bash
    python main.py
    ```

2. The application will run on `localhost` at port `8000`. You can change the host and port in the `main.py` file if needed.

### Usage

- **WebSocket Endpoint**: `/api/ws`

    - **Connect**: Establish a connection and initialize the server instance with a container ID.
    - **Stream Logs**: Continuously receive log updates from the specified Docker container.
    - **Execute Command**: Send commands to be executed on the Docker container.
    - **Heartbeat**: Maintain the WebSocket connection by sending periodic heartbeat messages.

### Example WebSocket Messages

#### Connect

```json
{
    "type": "connect",
    "server_id": "<your_container_id>"
}
```

#### Stream Logs

Once connected, logs will start streaming automatically.

#### Execute Command

```json
{
    "type": "command",
    "command": "<your_command>"
}
```

#### Heartbeat

```json
{
    "type": "heartbeat"
}
```

### Security

The WebSocket endpoint is protected by a custom `protected_route` decorator that checks for an `Authorization` header. Ensure to implement your token validation logic in `authentication.py`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## Contact

For any inquiries or feedback, please contact [Daftscientist](https://github.com/Daftscientist).
