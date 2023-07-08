function _fetch_qualified_projects_basic_info(conn::LibPQ.Connection)
    return execute(
            conn,
            """
            WITH t1 AS (
                SELECT main_info.*
                FROM qualified_projects
                LEFT JOIN main_info
                ON qualified_projects.project_id = main_info.project_id     
            )
            SELECT t1.*, projects.category, projects.start_time, projects.creator_id
            FROM t1
            LEFT JOIN projects
            ON t1.project_id = projects.project_id
            """) |> DataFrame
end

function _fetch_qualified_projects_reward_info(conn::LibPQ.Connection)
    df = execute(
        conn,
        """
        SELECT rewards.*
        FROM qualified_projects
        LEFT JOIN rewards
        ON qualified_projects.project_id = rewards.project_id
        """
    ) |> DataFrame
    return unique(df,[:project_id,:scraped_time,:reward_title])
end

function _fetch_qualified_projects_backer_info(conn::LibPQ.Connection)
    return execute(
        conn,
        """
        SELECT backers.*
        FROM qualified_projects
        LEFT JOIN backers
        ON qualified_projects.project_id = backers.project_id
        """
    ) |> DataFrame
end







"""
    fetch_qualified_projects_info(conn::LibPQ.Connection; reward_info=false,backer_info=false)

Fetch the information of qualified projects from the database.
If `reward_info` or `backer_info` is true, the relevant columns will be nested.
The detailed information of each column can be found in `create_tables.sql`
"""
function fetch_qualified_projects_info(conn::LibPQ.Connection; reward_info=false,backer_info=false)
    if !reward_info && !backer_info
        return _fetch_qualified_projects_basic_info(conn)
    elseif reward_info && !backer_info
        df1 = _fetch_qualified_projects_basic_info(conn)
        # There exists sveral duplicates due to previous crawler's bug
        unique!(df1,[:project_id,:scraped_time])
        # convert decimal values to Float64
        transform!(df1,
        [:goal,:pledged].=>ByRow(x->_convert_with_missing(Float64,x));
        renamecols=false)
        df2 = _fetch_qualified_projects_reward_info(conn)
        transform!(df2,
        :price=>ByRow(x->_convert_with_missing(Float64,x));
        renamecols=false)
        df = leftjoin(df1,df2,on=[:project_id,:scraped_time])
        # nest information from df2 to produce standard panel data
        return groupby(df,Cols(Not(names(df2)),:project_id,:scraped_time)) |> nest
    elseif !reward_info && backer_info
        df1 = _fetch_qualified_projects_basic_info(conn)
        # There exists sveral duplicates due to previous crawler's bug
        unique!(df1,[:project_id,:scraped_time])
        # convert decimal values to Float64
        transform!(df1,
        [:goal,:pledged].=>ByRow(x->_convert_with_missing(Float64,x));
        renamecols=false)
        df2 = _fetch_qualified_projects_backer_info(conn)
        dropmissing!(df2,:scraped_time)
        df = leftjoin(df1,df2,on=[:project_id,:scraped_time])
        # nest information from df2 to produce standard panel data
        return groupby(df,Cols(Not(names(df2)),:project_id,:scraped_time)) |> nest
    else
        df1 = fetch_qualified_projects_info(conn;reward_info=false,backer_info=true)
        df2 = fetch_qualified_projects_info(conn;reward_info=true,backer_info=false)
        shared_cols = intersect(names(df1),names(df2))
        return leftjoin(df1,df2,on=shared_cols)
    end
end