Anticheat System using Anomaly Detection
============================================

This is an open-source python project for showcasing Deep Learning capabilities for `Outlier Detection <https://en.wikipedia.org/wiki/Anomaly_detection>`_
and `Anomaly Detection <https://en.wikipedia.org/wiki/Anomaly_detection>`_.

The project contains trained **deep** models to detect anomalous client behaviour in server based sessions.

**Advantages of deep models**:

- **Adaptability** across the ever changing technologies that support these systems.
- **Versatility** of being applicable in a variety of environments, such as can be encountered in the current gaming industry.
- **Feature learning** that can be used to directly extract meaningful correlations that cannot be identified by humans. [#Nima2021]
- **Superior performance** compared to conventional machine learning models like Isolation Forests when it comes to unsupervised or semi-supervised learning in real-world tabular data.
- **Scalability** that is well-suited for big data applications and can take advantage of modern hardware like GPUs and TPUs to speed
  up training.

Installation
~~~~~~~~~~~~~~~
The project can be run locally via:

.. code-block:: bash


    $ git clone https://github.com/bananya-ml/anticheat.git
    $ cd anticheat
    $ pip install requirements.txt
    $ cd anticheat\serving\dashboard
    $ python app.py


Usages
~~~~~~~~~~~~~~~
Directly use the pre-trained models within the project:
::::::::::::::::::::::::::::::::::::::::::

The predictions can be made through the CLI or through a user friendly web app.

**for CLI:**

.. code-block:: bash

    $ cd .\anticheat\serving
    $ python main.py "dir-of-demo-to-be-analyzed"

**for starting a user friendly web-app:**

.. code-block:: bash


    $ cd .\anticheat\serving\dashboard
    $ python app.py

This will spin up a local web server. Create an account or sign in to upload a demo and view the results. The model may take upto **30 seconds** to generate results, depending on your machine.

Implemented Models
~~~~~~~~~~~~~~~~~~

In this project Deep SAD, from ICLR, 2020, for Deep Semi-Supervised Anomaly Detection has been trained to detect anomalies in processed real-world data. The library DeepOD [#Hongzuo2023Deepod]


NOTE:

- Due to hardware constraints, the model has been trained on over 7 million samples and 126 features from 460 unit samples. The training can easily be scaled up and trained on a much larger dataset, as it already uses best practices for utilizing GPU cores and parallel processing.

License
~~~~~~~~~~~~~~~

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License: MIT

.. include:: LICENSE



Reference
~~~~~~~~~~~~~~~~~

.. [#Nima2021] Nima Sedaghat, Martino Romaniello, Jonathan E Carrick, François-Xavier Pineau, Machines learn to infer stellar parameters just by looking at a large number of spectra, Monthly Notices of the Royal Astronomical Society, Volume 501, Issue 4, March 2021, Pages 6026–6041, https://doi.org/10.1093/mnras/staa3540

.. [#Hongzuo2023Deepod] Hongzuo Xu, Guansong Pang, Yijie Wang and Yongjun Wang, "Deep Isolation Forest for Anomaly Detection," in IEEE Transactions on Knowledge and Data Engineering, doi: 10.1109/TKDE.2023.3270293.


