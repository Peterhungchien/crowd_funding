# A Research Project on the Dynamics of Reward-Based Crowdfunding Campaigns

This repository is to store my code for scraping and analyzing the real-time crowdfunding campaign data from Modian, a Chinese website dedicated to publishing crowdfunding projects. 

There is now only code for scraping data and write them into databases. Several data analysis notebooks may be posted later. To run the code on your local machine, you need to have Julia installed. The scraper is now written in Python (A pure Julia implementation may be available later, or not :cold_sweat:), to call which in Julia requires [`PyCall.jl`](https://github.com/JuliaPy/PyCall.jl) and [`Conda.jl`](https://github.com/JuliaPy/Conda.jl) is necessary to install the Python packages. Other minor details you should pay attention to are commented in the scripts. To periodically scrape the data, I deployed the program on an Azure Virtual Machine and used crontab to schedule the task.

## About Reward-Based Crowdfunding and [Modian](https://www.modian.com/)
In a reward-based crowdfunding campaign, backers donate to a project they interested in and obtain non-financial rewards in return if the pledged amount reaches a certain threshold set by the entrepreneur. If the project fails, all thee given funds will be returned. Plus, many projects also set several stretch goals apart from the lowest threshold, which provide extra rewards if attained. A typical example of a crowdfunding project is a unreleased board game posted on [Kickstarter](https://www.kickstarter.com/). A board game lover may pre-purchase this game online at a price lower than the later list price and gain extra rewards such as mental game tokens or limited edition cards.

The uncertainty that the final return of a pledge depends on the total amount of money raised by a project engenders numerous intriguing questions: Does a higher goal contribute to a greater chance of success? Does more stretch goals necessarily attract more potential buyers? And the observed phenomena such as an "all or nothing" outcome are also worth investigating. 

The data used are scraped from [Modian](https://www.modian.com/), a Chinese analogue of Kickstarter but with a smaller size. This website lacks web scraping protection and has more detailed information concerning the backers of each project, thus is more suitable for web scraping.

## Datasets and Attributes
The detailed information of the five tables in my database is in `create_tables.sql`. You can use it to create the tables in your database.

## Model 0.1.0
I first attempted to build a one-period crowdfunding game where the total number and
the distribution of potential backers are known, and solved a separating equilibrium
in which all consumers have valuation higher than the price, but some choose not
to back due to uncertainty. The model specification is in `theory/Version_0_1_0/Version_0_1_0.tex`
and the simulation result is `script/theory/simu_version_0_1_0.html`.

## Next Step
1. Do some EDA to see if there is any interesting pattern.
2. Learn from literature (especially [this](https://cowles.yale.edu/research/cfdp-2149r-aiming-goal-contribution-dynamics-crowdfunding)).
3. Resort to my professor for suggestions.