FROM python
COPY requirements.txt /requirements.txt
COPY blink_timelapse.py /blink_timelapse.py
RUN pip3 install requests
RUN pip3 install -r /requirements.txt
CMD python3 /blink_timelapse.py