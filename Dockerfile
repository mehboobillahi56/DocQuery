# Use the official PostgreSQL image as a base
FROM postgres:latest

# Install necessary packages
RUN apt-get update && \
    apt-get install -y postgresql-server-dev-all build-essential git

# Create a non-root user to perform the build
RUN useradd -ms /bin/bash builder
USER builder

# Create a directory with appropriate permissions for the builder user
RUN mkdir -p /home/builder/pgvector

# Clone the pgvector repository and build the extension
RUN git clone https://github.com/pgvector/pgvector.git /home/builder/pgvector && \
    cd /home/builder/pgvector && \
    make

# Switch back to the root user to install the extension
USER root
RUN cd /home/builder/pgvector && make install

# Ensure that the extension is available in the PostgreSQL database
COPY init-db.sh /docker-entrypoint-initdb.d/

# Expose the default PostgreSQL port
EXPOSE 5432

# Set the default command to run PostgreSQL
CMD ["postgres"]
