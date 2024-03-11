FROM gitpod/workspace-full

# Install Anaconda
RUN wget --quiet https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /home/gitpod/anaconda && \
    rm ~/anaconda.sh && \
    echo "source /home/gitpod/anaconda/bin/activate" >> ~/.bashrc && \
    echo "conda init bash" >> ~/.bashrc
