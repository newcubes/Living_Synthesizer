trap 'echo -e "\nStopping monitor..."; killall rtl_433; exit' INT
/rtl_433 \
    -f 915M \
    -M level \
    -M report_meta \
    -M protocol \
    -R 123 \
    -Y autolevel \
    -C si \
    -F json:weather_data.json \
    -F csv:weather_data.csv \
    -F mqtt:127.0.0.1:1883

