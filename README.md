# IE Reader

## Installation
### Requirements

Running IE-Reader requires Docker and docker-compose for deployment 
and NodeJS for development.

[Docker-CE instalation documentation](https://docs.docker.com/install/)

[Docker-compose installation documentation](https://docs.docker.com/compose/install/).

One easy way to install docker-compose, once docker is installed,
is to use pip.

```bash
pip install docker-compose
```

### Deploying

The application can be deployed by running this command from the 
project's root directory:

```bash
docker-compose up
```

Then you can connect to the application by pointing your 
web browser to `http://localhost:3000`


#### Development

From the root of the directory, run:

```bash
docker-compose -f docker-compose-dev.yaml up
```

This will start a back-end only container listening on port 5000.

Then enter the front-end directory, `cd front-end`, and run:

```bash
npm install
npm start
```

This will start a development server that will connect to the 
backend and 

### Design documents
In the `./design-documents` folder are week-3 and week-6 milestone
reports. They contain initial UI wireframes and preliminary
data on normalizing the open information extraction process.
They also contain survey question from the SQUAD dataset
that was used to study the effects of IE-Reader on comprehension.

### User Study 

Pictures used in the user surveys are contained in the `./pics` directory
as well as a screenshot of the webapp. Statistical analysis of the 
user study data was performed with an Jupyter notebook in the `./analysis` 
directory. This directory also contains an image of box plots of user study responses. 
