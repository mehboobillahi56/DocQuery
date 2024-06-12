# Use the official PostgreSQL image as a base
FROM postgres:latest

# Install necessary packages
RUN apt-get update && \
    apt-get install -y postgresql-server-dev-all build-essential git

# Clone the pgvector repository and install the extension
RUN git clone https://github.com/pgvector/pgvector.git /usr/src/pgvector && \
    cd /usr/src/pgvector && \
    make && \
    make install

# Ensure that the extension is available in the PostgreSQL database
COPY init-db.sh /docker-entrypoint-initdb.d/

# Expose the default PostgreSQL port
EXPOSE 5432

# Set the default command to run PostgreSQL
CMD ["postgres"]
