# Use an official Python runtime as a parent image
FROM python:3.10.6

# Set the working directory in the container
WORKDIR /prod

# Copy the current directory contents into the container at /usr/src/app
COPY . /prod

# Install any needed packages specified in requirements_prod.txt
RUN pip install --no-cache-dir -r requirements_prod.txt

COPY streamlit_app.py /streamlit_app.py
COPY requirements_prod.txt /requirements_prod.txt

RUN pip install --upgrade pip
RUN pip install -r requirements_prod.txt

# Run fast.py when the container launches
CMD uvicorn fast:app --host 0.0.0.0
