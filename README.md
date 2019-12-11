# AI4E Container Example

### Install required packages

Ensure `git` and `git-lfs` are installed, and initialize git-lfs (e.g. for Mac):
```
# Update global git config
$ git lfs install

# Update system git config
$ sudo git lfs install --system
```

Install docker for your operating system: https://www.docker.com/get-started

### Build and run container

Replace `{your_username}` with your Docker username in the following commands:

- Build the container `docker build . -t {your_username}/ai4e-example:latest`
- Run the container locally: `docker run -p 8081:80 {your_username}/ai4e-example:latest`
- To run the API, `python client/test.py`
  - Requires `requests`
  - Should return: `True`
- To stop the container,

```
docker ps # grab the "CONTAINER ID"
docker stop {container_id}
```

## Contributing

- The `swagger.yaml` file is best edited via https://editor.swagger.io
