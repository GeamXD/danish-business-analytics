FROM gitpod/workspace-full

USER root

# Install Anaconda
ENV ANACONDA=Anaconda3-2022.05-Linux-x86_64.sh
RUN wget https://repo.anaconda.com/archive/${ANACONDA} && \
    bash ${ANACONDA} -b -p /opt/conda && \
    rm ${ANACONDA}

# Add conda to path
ENV PATH=/opt/conda/bin:$PATH

USER gitpod

# Create a conda environment
RUN conda create -n myenv python=3.8 -y

# Activate conda environment on start
RUN echo "source activate myenv" >> ~/.bashrc
