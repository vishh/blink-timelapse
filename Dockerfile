FROM python
RUN pip3 install requests astral opencv-python pytz absl-py
RUN git clone https://github.com/fronzbot/blinkpy.git && cd blinkpy && rm -rf build dist && python3 setup.py bdist_wheel && pip3 install --upgrade dist/*.whl && cd .. 
RUN cp /usr/share/zoneinfo/US/Pacific /etc/localtime
COPY blink_timelapse.py /blink_timelapse.py
COPY copy-files.py /copy-files.py
CMD python3 /blink_timelapse.py