-- @block Find qualified projects
-- @conn remote_crowd_funding
-- (The above lines specify the chunk options of SQLtools extension. Just ingore them.)
CREATE VIEW qualified_projects AS
SELECT covered.project_id
FROM(
    -- Find fully covered projects
    SELECT p.project_id
    FROM projects p
      JOIN (
        SELECT project_id,
          MIN(scraped_time) AS min_scraped_time,
          MAX(scraped_time) AS max_scraped_time
        FROM main_info
        GROUP BY project_id
      ) mi ON mi.project_id = p.project_id
      JOIN (
        SELECT project_id,
          MAX(end_time) AS max_end_time
        FROM main_info
        GROUP BY project_id
      ) mi2 ON mi2.project_id = p.project_id
    WHERE mi.min_scraped_time <= p.start_time + INTERVAL '12 hours'
      AND mi.max_scraped_time >= mi2.max_end_time
  ) covered
  INNER JOIN (
    -- Find projects whose scraping did not crashed
    -- (i.e. the time difference between two consecutive scraping is less than 1 day)
    SELECT project_id
    FROM (
        SELECT project_id,
          mi.scraped_time - LAG(mi.scraped_time, 1) OVER (
            PARTITION BY mi.project_id
            ORDER BY mi.scraped_time
          ) AS time_diff
        FROM main_info mi
      ) subquery
    GROUP BY project_id
    HAVING MAX(time_diff) < INTERVAL '1 day'
  ) within_1d ON within_1d.project_id = covered.project_id;