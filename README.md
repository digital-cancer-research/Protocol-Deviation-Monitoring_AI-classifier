# Protocol Deviation Monitoring - AI classifier

## Requirements

- Python 3.7+
- pip

## Installation

1) Download or clone the [*repository*](https://github.com/digital-cancer-research/qa-ai/tree/main) to your local machine. 
2) In the base directory of the cloned repository, navigate to the `pdai` directory :
		`cd pdai`  
3) Run the `pip` command with the parameters below:
		`pip install .`
		
> [!CAUTION]
>  Please note that the last character in the command is a period (.)
  
  Once all dependencies are installed, the PD classifier is ready to use.

## Startup

To start the system, run the following command:

`python pdai/app.py <listening_address> <listening_port>`

> [!Note]
> Depending on your operating system (OS), it may be possible to integrate this command as an OS service. Requirements will vary based on the host server’s configuration.. 

The parameters `<listening_address>` and `<listening_port>` specify the server address and the IP port that will listen for incoming requests. Additionally, the classifier only processes `POST` requests made to the `/prediction` endpoint. Calls to any other path or using a different request method will return an error message.

If these parameters are not provided, the server will listen on the host's IP address and port `8088`.

> [!CAUTION]
> Parameters must be provided in the specified order. If you need to run the service on a different IP address but use the default port, only the first parameter should be specified. If the service needs to run on a different port while using the default IP address, both parameters must be provided. Failure to adhere to these requirements may result in an error.

The service will continue running and will send messages to the console indicating its activity:

```
Starting application on 0.0.0.0:8088!
INFO:     Started server process [5226]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8088 (Press CTRL+C to quit)
INFO:     127.0.0.1:52985 - "POST /prediction HTTP/1.1" 200 OK
INFO:     127.0.0.1:53569 - "POST /prediction HTTP/1.1" 200 OK
```

The PD classifier will stop when the `CTRL+C` keys are pressed or when the operating system prompt returns to the user for any other reason. A message like the following may appear.

```
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [5226]
```

The status of the PD classifier can be monitored by checking the process number indicated in the line `INFO: Started server process [process_number]`, where the `process_number` corresponds to the identifier assigned to the server.

## Testing

To validate the service, you can send a query to the server as outlined in the user's guide.
