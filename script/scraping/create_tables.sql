-- This sql script is to create the five tables to store the scraped data.
-- Meanings of each columns are listed below. If a column appears in multiple tables, its meaning
-- is written only once.

-- This table has the information of each project that is invariant over time.
-- project_id: a unique identifier for the project, reflected in its URL.
-- category: the category of the project in Chinese.
-- start_time: the start date of the project.
-- creator_id: the id of the initiator of the project.
CREATE TABLE projects(
    project_id VARCHAR(10) PRIMARY KEY NOT NULL,
    category VARCHAR(10),
    start_time TIMESTAMP,
    creator_id VARCHAR(20)
);

-- This table stores the time-varying information of each project except the details of its rewards.
-- goal: the goal of the project in Chinese Yuan.
-- pledged: the amount the project realized at the scraped time.
-- backer_num: the number of supporters that had invested in the project at the scraped time.
-- status: whether the project was active at the scraped time.
-- end_time: the end date of the project (It is subject to change in the course of a campaign.).
-- update_num: the number of updates the project had made at the scraped time.
-- attention: the number of platform users that had "liked" the project at the scraped time.
-- comment_num: the number of comments under the project page at the scraped time.
-- scraped_time: the time when the crawler was started.

CREATE TABLE main_info(
    project_id VARCHAR(10) NOT NULL,
    goal NUMERIC,
    pledged NUMERIC,
    backer_num INT,
    status BOOLEAN,
    end_time TIMESTAMP,
    update_num INT,
    attention INT,
    comment_num INT,
    scraped_time TIMESTAMP
);

-- This table lists the backers supporting a project at a certain time and the total number of
-- project each backer had invested into.
-- backer_id: the id of the backer.
-- support_num: the number of projects the backer had supported at the scraped time.

CREATE TABLE backers(
    backer_id VARCHAR(20),
    project_id VARCHAR(10) NOT NULL,
    support_num INT,
    scraped_time TIMESTAMP
);

-- This table records which projects were listed on the front page of the website 
-- at the scraped time. Being featured 

CREATE TABLE front_page(
    project_id VARCHAR(10) NOT NULL,
    scraped_time TIMESTAMP NOT NULL
);

-- This table records the title of each reward of a project, its price, how many of
-- it had been sold at the scraped time and whether it had a purchase limit.
-- reward_title: the title of the reward.
-- price: the price of the reward.
-- quantity: the number of the reward purchased at the scraped time.
-- quantity_limit: the largest number of the reward that can be pre-purchased. This column is 0
-- if there is no limit.

CREATE TABLE rewards(
    project_id VARCHAR(20) NOT NULL,
    reward_title VARCHAR(100),
    price NUMERIC,
    quantity INT,
    quantity_limit INT ,
    scraped_time TIMESTAMP NOT NULL
);