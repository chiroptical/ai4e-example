# AI4E Container Example

### Install required packages

* `git` and `git-lfs` (for storing large files): https://help.github.com/en/github/managing-large-files/installing-git-large-file-storage
* Docker: https://www.docker.com/get-started
* Python libraries `requests` and `pytest`

### Docker
Replace `{your_username}` with your Docker username in the following commands: 

- Build the container `docker build . -t {your_username}/ai4e-example:latest`
- Run the container locally: `docker run -p 8081:80 {your_username}/ai4e-example:latest`
- Run the tests using `pytest` from the root directory
  - Requires `requests` and `pytest`
- To stop the container,

```
docker ps # grab the "CONTAINER ID"
docker stop {container_id}
```

## Contributing

- The `swagger.yaml` file is best edited via https://editor.swagger.io
