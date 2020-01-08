# AI4E Container Example

### Obtain requirements

* Install `git` and `git-lfs` (for storing large files): https://help.github.com/en/github/managing-large-files/installing-git-large-file-storage
* Install Docker: https://www.docker.com/get-started
* Install Python libraries `requests` and `pytest`
* Please contact authors to obtain models and build the container yourself, it requires:
  - `./models/model_passerines.h5`
  - `./models/model_nonpasserines.h5`

### Docker

Replace `{your_username}` with your Docker username in the following commands: 

- Build the container `docker build . -t {your_username}/ai4e-example:latest`
- Run the container locally: `docker run -p 8081:80 {your_username}/ai4e-example:latest`
- In another terminal window, run the tests using `pytest` from the root directory
- To stop the container, in another terminal window, run:

```
docker ps # grab the "CONTAINER ID"
docker stop {container_id}
```

## Contributing

- The `openapi.yaml` file is best viewed via https://editor.swagger.io
