from python:3.9-slim
WORKDIR /app    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 
# Declare a build-time argument for the Git commit hash.
ARG GIT_COMMIT_HASH=unspecified
# Add a label to the image using the OCI standard format.
LABEL org.opencontainers.image.revision=$GIT_COMMIT_HASH
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
