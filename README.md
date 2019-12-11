# AI4E Container Example

- Build the container `docker build . -t barrymoo/ai4e-example:latest`
- Run the container locally: `docker run -p 8081:80 barrymoo/ai4e-example:latest`
- To run the API, `python client/test.py`
  - Requires `requests`
  - Should return: `True`
