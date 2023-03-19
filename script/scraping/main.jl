using LibPQ
using DataFrames
using DataFramesMeta
using PyCall
using Dates

function write_db(df::DataFrame;conn::LibPQ.Connection,tbl_name::AbstractString,no_nulls::Array{Symbol,1})
    row_strings = map(eachrow(df)) do row
        row_string = ""
        col_symbols = Symbol.(names(row))
        for col in col_symbols
            if ismissing(row[col])
                col in no_nulls && throw(ArgumentError("Column $col missing in row $row"))
            else
                col == last(col_symbols) ? row_string*="$(row[col])\n" : row_string*="$(row[col]),"
            end
        end
        row_string
    end

    copyin = LibPQ.CopyIn("COPY $tbl_name FROM STDIN (FORMAT CSV);", row_strings)
    execute(conn,copyin)
end



function main()
    scraped_time = now()
    println("Scraping job started at $scraped_time")
    connection_string = read(open("script/scraping/connection_string.txt"),String)

    # get the list of potentially active projects from the main_info database
    # get the projects scraped last time
    conn = LibPQ.Connection(connection_string)
    prev_project_id = @chain begin
        execute(conn,
        """
        SELECT project_id 
        FROM main_info a
        WHERE a.scraped_time = (SELECT MAX(scraped_time) FROM main_info)
        """)
        DataFrame(_)
        _[!,:project_id]
    end
    # get the project-backer pairs that have already been scraped.
    prev_project_backer_pair = @chain begin
        execute(conn,
        """
        SELECT project_id, id
        FROM backers
        """)
        DataFrame(_)
        zip(_[:,:project_id],_[:,:id])
        collect(_)
    end
    # scrape the ids of currently activate projects
    py"""
    import sys
    sys.path.append("script/scraping")
    """
    md = pyimport("modian")
    scraper = md.ModianScraper()
    active_project_id = scraper.get_active_pro()
    project_id_to_add = setdiff(Set(active_project_id),Set(prev_project_id)) |> collect
    project_to_scrape = vcat(prev_project_id,active_project_id)
    # scrape the main information of each project (including detailed reward information)
    main_info_vec = [scraper.get_main_info(pro) for pro in project_to_scrape]
    main_info_df = vcat(DataFrame.(main_info_vec)...)
    # separate the main_info df
    main_info_reward_excluded = @chain begin
        main_info_df
        select(_,Not(:reward_info))
        @distinct _
        @rtransform(_,:status=:project_id in active_project_id)
    end
    reward_info = @chain begin
        main_info_df
        select(_,:project_id,:reward_info)
        transform(_,:reward_info .=> 
        ByRow.([x -> x[i] for i in 1:4]) 
        .=> [:reward_title,:price,:quantity,:quantity_limit])
        select(_,Not(:reward_info))
    end
    front_page_project_id = scraper.get_front_page()
    backer_each_project = map(project_to_scrape) do pro
        dict = scraper.get_backer_list(pro)
        dict["project_id"] = pro
        dict
    end
    backer_df = @chain begin
        vcat(DataFrame.(backer_each_project)...)
        @select(:id=:uid,:support_num=:pro_supported,:project_id)
    end

    # write the scraped data into database
    backers_to_write = @chain begin
        backer_df
        @rsubset(_,!((:project_id,:id) in prev_project_backer_pair))
        @select(_,:id,:project_id,:support_num)
    end

    # add project_id key to each dict in this vector
    # add scraped_time column to create the final df's to write
    front_page_to_write = DataFrame(Dict("project_id"=>front_page_project_id,
    "scraped_time"=>scraped_time))
    # helper function to add a scraping time column
    function add_scraped_time(df::DataFrame,time_stamp::DateTime)
        new_df = copy(df)
        new_df[!,:scraped_time] .= time_stamp
        return new_df
    end
    main_info_to_write = @chain begin
        main_info_reward_excluded
        add_scraped_time(_,scraped_time)
        @select(:project_id,:goal,:backer_money,:backer_num,
        :status,:end_time,:update_num,:attention,
        :comment_num,:scraped_time)
    end
    rewards_to_write = add_scraped_time(reward_info,scraped_time)
    projects_to_write = @chain begin
        main_info_reward_excluded
        @select(_,:id=:project_id,:category,:start_time,:creator_id)
        @rsubset(_,:id in project_id_to_add)
    end

    # write into database
    write_db(projects_to_write,conn=conn,tbl_name="projects",
    no_nulls=[:id])
    write_db(main_info_to_write,conn=conn,tbl_name="main_info",
    no_nulls=[:project_id])
    write_db(backers_to_write,conn=conn,tbl_name="backers",
    no_nulls=[:id,:project_id])
    write_db(front_page_to_write,conn=conn,tbl_name="front_page",
    no_nulls=[:project_id,:scraped_time])
    write_db(rewards_to_write,conn=conn,tbl_name="rewards",
    no_nulls=[:project_id,:reward_title,:scraped_time])
    println("Scraping job succeeded at $scraped_time")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
