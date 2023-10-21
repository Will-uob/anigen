# anigen
Hello, welcome to anigen. This is a deployable social media app which allows users to generate images of anime girls using the "waifu-diffusers" model from HuggingFace diffusers! To run, you should have mamba installed, or you can manually install the
packages in requirements.txt using pip. I highly recommend using a virtual environment for this purpose.

After installing the required packages, you can initiate the project using the command
```
flask --app anigen init-db
```
and then run the application using
```
flask --app anigen run --debug
```
for testing purposes. I will update this README.md in the future to cover deployment, as well as any other dependencies that are required.
