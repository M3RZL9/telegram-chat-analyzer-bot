#!/bin/bash

# Start the Docker container
start_container() {
    echo "Starting tg_analyzer_bot_container..."
    docker start tg_analyzer_bot_container
}

# Stop the Docker container
stop_container() {
    echo "Stopping tg_analyzer_bot_container..."
    docker stop tg_analyzer_bot_container
}

# Main function
main() {
    case "$1" in
        start)
            start_container
            ;;
        stop)
            stop_container
            ;;
        *)
            echo "Usage: $0 {start|stop}"
            exit 1
            ;;
    esac
}

# Run the main function with the provided arguments
main "$@"

#chmod +x tg_bot_control.sh
