FROM gitpod/workspace-full

# Install Anaconda
RUN wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh -O ~/anaconda.sh \
    && bash ~/anaconda.sh -b -p $HOME/anaconda \
    && rm ~/anaconda.sh \
    && echo "source $HOME/anaconda/bin/activate" >> ~/.bashrc

# Initialize Conda in bash shell by default
ENV BASH_ENV=~/.bashrc
SHELL ["/bin/bash", "-c"]
