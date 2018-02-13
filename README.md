# Python2.7-MAESC
A repo for building a Python 2.7 microservice Docker image

## Build

Build the image with `build.sh`. Pass in your hostname as an argument (i.e. HOSTNAME/python2.7)

## Running

You can run the image with the following command (replace HOST_PORT,HOST_DIR,HOST_NAME):

`docker run -itd -p HOST_PORT:9602 HOST_NAME/python2.7`

## Usage

/service - this will run your Python 2.7 code and respond with your requested variables.

```
{
  "code": string, the code to run
  "vars": array, should contain the variable names from your code that you want returned
}

* if your variable points to a resource (i.e. image,audio,etc.), it should start with an underscore "_". When /service returns that variable, it will point to the URL where that resource can be retrieved.
