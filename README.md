# A Research Project on the Dynamics of Reward-Based Crowd Funding Campaigns

This repository is to store my code for scraping and analyzing the real-time crowd funding campaign data from modian.com, a Chinese website dedicated to publishing crowd funding projects. 

There is now only code for scraping data and write them into databases. Several data analysis notebooks may be posted later. To run the code on your local machine, you need to have Julia installed. The scraper is now written in Python, to call which in Julia requires [`PyCall.jl`](https://github.com/JuliaPy/PyCall.jl) and [`Conda.jl`] is necessary to install the Python packages. Other minor details you should pay attention to are commented in the scripts.