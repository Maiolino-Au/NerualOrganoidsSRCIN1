docker run \
    --runtime=nvidia -it --rm \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    -p 8888:8888 \
    -v .:/sharedFolder \
    -v /home/$USER/Documents/python:/python \
    -v /home/$USER/Documents/organoidi_2024/data_organoidi_velasco:/data_organoidi_velasco \
    -v /home/$USER/Documents/organoidi_2024/data_bersia/hnoca_scvi_model:/hnoca_scvi_model \
    neuralorganoidssrcin1:1.0.0
