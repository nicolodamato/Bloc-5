FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update -y 
RUN apt-get install nano unzip
RUN apt-get install -y python3.10
RUN apt install curl -y

RUN curl -fsSL https://get.deta.dev/cli.sh | sh

COPY requirements.txt /dependencies/requirements.txt
RUN conda install -c conda-forge shap psutil && pip install -r /dependencies/requirements.txt

COPY . /home/app

CMD gunicorn app:app  --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker


# Deployement on Heroku
# heroku login
# heroku container:login
# heroku create predict-getaround-nico
# docker buildx build --platform linux/amd64 -t predict-getaround .
# docker tag predict-getaround registry.heroku.com/predict-getaround-nico/web
# docker push registry.heroku.com/predict-getaround-nico/web
# heroku container:release web -a predict-getaround-nico
# heroku open -a predict-getaround-nico