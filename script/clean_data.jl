using DataFrames
using DataFramesMeta
using CSV
using Dates
using TimeZones

# helper functions

function parse_datetime(s)
    dt_pattern = r"\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}"
    return DateTime(match(dt_pattern, s).match,"yyyy-mm-dd HH:MM:SS")
end

function convert_time_zone(t::DateTime)
	zoned_t=ZonedDateTime(t,TimeZone("US/Pacific",TimeZones.Class(:LEGACY)))
	return astimezone(zoned_t,tz"Asia/Shanghai") |> DateTime
end

function compute_time_difference(t1::DateTime,t2::DateTime,unit::TimePeriod)
	raw_diff = t1-t2
	return raw_diff/unit |> ceil |> Int
end

function diff_pledged(elapsed_vec,pledged_vec)
	diff_pledged = diff(vcat([0],pledged_vec))
	diff_elapsed = diff(vcat([0],elapsed_vec))
	return map((x,n)->x/n,diff_pledged,diff_elapsed)
end




function main()
    main_info_df = DataFrame(CSV.File("data/prev_data/merged_main_info_df.csv"))

    # drop missing values
    dropmissing!(main_info_df)

    # convert column types
    @chain main_info_df begin
        transform!(_,
        [:start_time,:end_time,:scraped_time].=>ByRow(parse_datetime)
        .=>[:start_time,:end_time,:scraped_time],
        [:project_id,:creator_id].=>ByRow(x->string(Int(x)))
        .=>[:project_id,:creator_id],
        :status=>(x-> x.=="active")=>:status)
    end

    # convert time zones
    transform!(main_info_df,:scraped_time=>ByRow(convert_time_zone)=>:scraped_time)

    # filter projects
    subset!(main_info_df,
    [:start_time,:end_time,:scraped_time]
    =>(x,y,z)->((x.>=minimum(z)).&&(y.<=maximum(z))))

    # length and elapsed
    @transform!(main_info_df,
    :project_length=compute_time_difference.(:end_time,:start_time,Hour(12)),
    :elapsed=compute_time_difference.(:scraped_time,:start_time,Hour(12)))

    # exclude projects with varying project length from the sample
    @chain main_info_df begin
        groupby(_,:project_id)
        subset!(_,:project_length=>(x->maximum(x)==minimum(x)))
    end

    # obtain outcomes
    @chain main_info_df begin
        sort!(_,:scraped_time)
        groupby(_,:project_id)
        transform!(_,[:goal,:pledged]=>((x,y)->last(x)<=last(y))=>:success)
    end

    @chain main_info_df begin
        sort!(_,:elapsed)
        groupby(_,:project_id)
        transform!(_,[:elapsed,:pledged]=>diff_pledged=>:diff_pledged)
    end

    # summarise the outcomes
    outcome = @chain main_info_df begin
        sort(_,:scraped_time)
        groupby(_,:project_id)
        combine(_,
        Not([:scraped_time,:elapsed,:diff_pledged]).=>last
        .=>Not([:scraped_time,:elapsed,:diff_pledged]))
        subset(_,:status=>ByRow(!)) # For some projects, the snapshot of its end was not captured.
        select(_,Not(:status))
    end

    return main_info_df, outcome

end

if abspath(PROGRAM_FILE) == @__FILE__
    main_info_cleaned, outcome = main()
    #CSV.write("data/prev_data/main_info_cleaned.csv", main_info_cleaned)
    #CSV.write("data/prev_data/outcome.csv",outcome)
end