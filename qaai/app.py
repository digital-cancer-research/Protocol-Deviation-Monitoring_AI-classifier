import uvicorn
import sys


def run_app(address: str = "0.0.0.0", port: int = 8088):
    print(f"Starting application on {address}:{port}!")
    uvicorn.run("api:app", host=address, port=port, reload=False, log_level="info")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_app()
    elif len(sys.argv) == 2:
        run_app(address=str(sys.argv[1]))
    elif len(sys.argv) == 3:
        run_app(address=str(sys.argv[1]), port=int(sys.argv[2]))
    else:
        raise AttributeError("Expected <address> and <port> as attributes!")
