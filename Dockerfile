FROM python
COPY blink_timelapse.py /blink_timelapse.py
RUN pip3 install requests astral opencv-python pytz
RUN git clone https://github.com/fronzbot/blinkpy.git && cd blinkpy && rm -rf build dist && python3 setup.py bdist_wheel && pip3 install --upgrade dist/*.whl && cd .. 
CMD python3 /blink_timelapse.py