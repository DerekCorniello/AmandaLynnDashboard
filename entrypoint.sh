#!/bin/sh

# Check if the database file exists in the container
if [ ! -f /app/${DATABASE_NAME} ]; then
  # If it doesn’t exist, create a fresh copy or initialize it if needed
  cp /app/${DATABASE_NAME}.backup /app/${DATABASE_NAME}
fi

# Run the CMD as the container's main process
exec "$@"
