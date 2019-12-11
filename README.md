# AI4E Container Example

### Setup

Ensure `git` and `git-lfs` are installed, and initialize git-lfs.
```
# Update global git config
$ git lfs install

# Update system git config
$ sudo git lfs install --system
```

### Docker
- Build the container `docker build . -t barrymoo/ai4e-example:latest`
- Run the container locally: `docker run -p 8081:80 barrymoo/ai4e-example:latest`
- Run the tests using `pytest` from the root directory
  - Requires `requests` and `pytest`
- To stop the container,

```
docker ps # grab the "CONTAINER ID"
docker stop {container_id}
```

## Contributing

- The `swagger.yaml` file is best edited via https://editor.swagger.io
