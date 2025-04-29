# E-Scooter Rental System (TTM4115 Komsys Project)

This project implements a simplified e-scooter rental system consisting of a web application frontend, simulated e-scooter backends, and a central server component, all communicating via MQTT. The system utilizes state machines (`stmpy`) to manage the application and scooter states.

## Features

-   **Web Frontend (Flask):**
    -   Displays a list of available scooters fetched dynamically via MQTT.
    -   Shows scooter details like battery level (simulated) and location (simulated).
    -   Calculates and displays the distance to each scooter (requires browser location permissions).
    -   Allows users to:
        -   **Unlock:** Start renting a scooter directly.
        -   **Reserve:** Reserve a scooter for a short period before unlocking.
        -   **Lock:** End the rental period.
        -   **Report:** Report a scooter for poor driving behaviour.
    -   Displays flash messages for success, errors, timeouts, and the final bill.
    -   Uses polling with timeouts to wait for scooter responses (e.g., `unlock_ok`, `lock_ok`).
-   **E-Scooter Backend:**
    -   Simulates individual e-scooters.
    -   Each scooter runs its own state machine (idle, reserved, unlocked, driving).
    -   Responds to `unlock`, `lock`, `reserve`, and `report` actions received via MQTT.
    -   Publishes its status (availability, location, battery) via MQTT.
    -   Calculates a bill upon locking, considering:
        -   Distance travelled (simulated).
        -   Cost per km.
        -   Reservation time and cost per minute.
        -   Discount for parking while charging (simulated via USB detection if on RPi).
        -   Penalty multiplier if reported by another user.
    -   **(Optional Raspberry Pi Integration):**
        -   Can utilize a Sense HAT for visual feedback (lock/unlock icons, driving animation).
        -   Uses the Sense HAT IMU to check if the scooter is parked correctly (within pitch/roll thresholds) before allowing locking.
        -   Uses USB detection (`lsusb`) to determine if the scooter is charging.
        -   Plays a sound effect (`sound2.wav`) when "driving".
-   **Server Component:**
    -   Listens for scooter status updates via MQTT.
    -   Maintains a dictionary of known scooters and their status.
    -   Responds to requests from the frontend (`gr8/server/scooter_list`) by publishing the current list of known scooters (`gr8/scooters/scooter_list`).

## Architecture

The system follows a publish-subscribe pattern using an MQTT broker (`mqtt20.iik.ntnu.no:1883`) as the central communication hub.

1.  **E-Scooters (`escooter/`)**: Each scooter instance connects to the MQTT broker. It subscribes to its specific action topic (`gr8/scooters/action/{scooter_id}`) and publishes its status to a general topic (`gr8/scooters/status`). It also publishes responses (like `unlock_ok`, `lock_ok`, `bill`) directly back to its specific topic (`gr8/scooters/{scooter_id}`).
2.  **Server (`server/`)**: The server connects to the MQTT broker. It subscribes to the general scooter status topic (`gr8/scooters/status`) to build its list of known scooters. It also subscribes to a specific server request topic (`gr8/server/scooter_list`) to listen for requests from the frontend. When requested, it publishes the known scooter list to `gr8/scooters/scooter_list`.
3.  **Frontend Application (`application/frontend/`)**: The Flask application connects to the MQTT broker. It subscribes to the scooter list topic (`gr8/scooters/scooter_list`) and the general status topic (`gr8/scooters/status`) to get updates. It also subscribes to the specific topic of the _active_ scooter (`gr8/scooters/{active_scooter_id}`) to receive confirmations (`unlock_ok`, `lock_ok`, etc.) and error messages. It publishes actions (`unlock`, `lock`, `reserve`, `report`) to the specific scooter's action topic (`gr8/scooters/action/{scooter_id}`) and requests the scooter list by publishing to the server topic (`gr8/server/scooter_list`).

## Technology Stack

-   **Backend:** Python 3
-   **Web Framework:** Flask
-   **State Machines:** `stmpy`
-   **Communication:** `paho-mqtt` (MQTT)
-   **Frontend:** HTML, CSS, JavaScript
-   **(Optional):** Raspberry Pi, Sense HAT (`sense-hat` library)
-   **(Optional):** Pygame (`pygame` library for sound)
-   **Testing:** Jupyter Notebook

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ttm4115-komsys-project-main
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Linux/macOS
    source .venv/bin/activate
    # On Windows
    .\.venv\Scripts\activate
    ```
3.  **Install dependencies:**

        ```bash
        pip install -r requirements.txt
        ```

    _(Note: If using Raspberry Pi features, ensure `sense-hat` and/or `pygame` are uncommented/added and installed. You might need additional system libraries for Pygame.)_

4.  **MQTT Broker:** The project is configured to use `mqtt20.iik.ntnu.no` on port `1883`. Ensure you have network access to this broker.

## Running the Project

Run each component in a separate terminal window. Make sure the virtual environment is activated in each terminal. If you are using the Raspberry Pi features, ensure that the `run_scooters.py` script is run on the Raspberry Pi.

1.  **Start the Server:**

    ```bash
    python run_server.py
    ```

    _(Output: `Server connected to broker`)_

2.  **Start the E-Scooters:**

-   Configure which scooters to run by editing the flags in `run_scooters.py`.

    -   `ADD_SENSEHAT_SCOOTER` (True if using Raspberry Pi with Sense HAT)
    -   `ADD_THREE_SCOOTERS`(True if you want to run 3 scooters)
    -   `ADD_EXTRA_SCOOTER` (True if you want to add an extra scooter)

-   Run the script:
    ```bash
    python run_scooters.py
    ```
    _(Output: Connection messages for each started scooter)_

3.  **Start the Frontend Application:**

    ```bash
    flask run application/frontend/app.py
    ```

    _(Output: Flask development server startup messages, typically ending with `Running on http://127.0.0.1:5015`)_

4.  **Access the Web Application:** Open your web browser and navigate to `http://127.0.0.1:5015`.

## Usage

1.  Open the web application in your browser.
2.  Allow location access if prompted to see distances to scooters.
3.  The index page (`/`) shows available scooters near you.
4.  Click **"Unlock"** to attempt renting a scooter immediately. If successful, you'll be redirected to the `/active` page.
5.  Click **"Reserve"** to reserve a scooter. If successful, you'll be redirected to the `/reserve` page. From there, you can click **"Unlock"** to start riding.
6.  On the `/active` page, click **"Lock"** to end your ride. You will be redirected back to the index page, and a bill summary will be displayed if the lock was successful.
7.  On the index page, you can enter a scooter ID and click **"Report"** to simulate reporting a user for poor driving. This will affect their final bill.
