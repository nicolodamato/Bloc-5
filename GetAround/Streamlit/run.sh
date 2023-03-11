docker run -it\
 -v "$(pwd):/home/app"\
 -e PORT=80\
 -p 4000:80\
 streamlit
