FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update
RUN apt-get install nano unzip
RUN apt install curl -y

RUN curl -fsSL https://get.deta.dev/cli.sh | sh
RUN pip install boto3 pandas gunicorn streamlit sklearn matplotlib seaborn plotly joblib openpyxl
COPY . /home/app

CMD streamlit run --server.port $PORT app.py


# Deployement on Heroku
# heroku login
# heroku container:login
# heroku create streamlit-getaround-nico
# docker buildx build --platform linux/amd64 -t streamlit-getaround .
# docker tag streamlit-getaround registry.heroku.com/streamlit-getaround-nico/web
# docker push registry.heroku.com/streamlit-getaround-nico/web
# heroku container:release web -a streamlit-getaround-nico
# heroku open -a streamlit-getaround-nico