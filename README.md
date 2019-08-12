# AI4E Container Example

- Build the container `docker build . -t barrymoo/ai4e-example:latest`
- Run the container locally: `docker run -p 8081:80 barrymoo/ai4e-example:latest`
- To run the API, `cd client` and `python post_audio_data.py`
  - Should return: `{"image_size":[256,256]}`
