# Tested with this specified Python version. Using a different version may cause errors.
FROM python:3.9.20-bullseye

# Local application directory.
WORKDIR /Users/mromero/PycharmProjects/qa-ai

# Prerequisite for installing one of the requirements.
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Copy the entire project to the container.
COPY . .

# Installing the application on the container.
RUN . $HOME/.cargo/env && pip install wheel &&  python -m pip install --upgrade pip  && pip install .


COPY . .

# Starting the application on the container.
CMD [ "python", "./qaai/app.py" ]

# Exposing the application's port.
EXPOSE 8088/tcp


# Build command:
# $ docker --debug build -t qaai .