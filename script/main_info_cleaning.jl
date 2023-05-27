#%% ---
#%% title: Clean the main information CSV file scraped before
#%% ---
#%% To save the space and make my code more manageable,
#%% I put the convenience functions in a module and import them.
using DataFrames, Chain
using CSV, JLD2
using Printf
using Dates
using Crowdfunding: parse_datetime, convert_time_zone, compute_time_index
using Crowdfunding: parse_price_quantity_string, compute_avg_price
using Crowdfunding: complete, interpolate_missing_linear, fill_missing
project_dir = dirname(@__DIR__)
#+ 
main_info_df = CSV.read("$project_dir/data/prev_data/merged_main_info_df.csv",DataFrame)
describe(main_info_df)
#%% ## Check missing values
subset(main_info_df,All()=>ByRow((x...)->any(ismissing,x)))
#%% These missing values are due to the bugs of the crowdfunding websites.
#%% Just drop them.
dropmissing!(main_info_df)
#%% ## Convert column types
Base.show(io::IO, f::Float64) = @printf(io, "%.0f", f) # ids are misinterpreted as floats
transform!(main_info_df,
[:project_id,:creator_id].=>x->repr.(x),
:status=>x->x.=="active";
renamecols=false)
#%% convert time zone
transform!(main_info_df,
[:start_time,:end_time].=>ByRow(parse_datetime),
:scraped_time=>ByRow(x->parse_datetime(x)|>convert_time_zone);renamecols=false)
#%% ## Compute average price
#%% Next we parse the [(price,quantity purchased)] column to convert them into vectors of tuples.
#%% After the conversion, compute the average price of the goods.
#%% If the number of goods is more than two, remove the highest and lowest value first.
#%% (This approach is flawed though,
#%% since a project may have several expensive options tailored for few generous donors.
#%% From this perspective, the average price should be weighted by the quantity purchased.
#%% This however involves reverse causality.)
@chain main_info_df begin
    transform!(_,:price_quantity=>ByRow(parse_price_quantity_string);renamecols=false)
    transform!(_,:price_quantity=>ByRow(compute_avg_price)=>:avg_price)
end
#%% ## Create discrete time index
#%% we can divide the time passed from the commencement of a project by 12 hours
#%% and take ceiling to get the time index.
@chain main_info_df begin
    groupby(_,:project_id)
    transform!(_,
    [:scraped_time,:start_time]=>((x,y)->compute_time_index(x,first(y);unit=Hour(12)))=>:time_index)
end
#%% check if there are duplicated time index
@chain begin
    nonunique(main_info_df,[:project_id,:time_index])
    main_info_df[_,:]
end
#%% It turns out that for some projects have multiple observations
#%% within 12 hours. For those data, we only keep
#%% the latest observations in a 12-hour window.
@chain main_info_df begin
    sort!(_,:scraped_time)
    unique!(_,[:project_id,:time_index];keep=:last)
end
#%% ## Filter projects
# Only keep projects whose life cycle is fully covered
@chain main_info_df begin
    sort!(_,:time_index)
    groupby(_,:project_id)
    subset!(_,
    :time_index=>x->minimum(x)==1,
    [:end_time,:scraped_time]=>((x,y)->last(x)<=last(y)))
end
#+
# Check if the project end date is modified halfway
@chain main_info_df begin
    groupby(_,:project_id)
    subset(_,:end_time=> x-> maximum(x) != minimum(x))
end
#+
# Remove these projects
@chain main_info_df begin
    groupby(_,:project_id)
    subset!(_,:end_time=> x-> maximum(x) == minimum(x))
end
#%% Interpolate missing values
# complete data for each project by time index
main_info_df = @chain main_info_df begin
    groupby(_,:project_id)
    complete(_,:time_index)
end
#+
# forward fill the time-invariant variables
# interpolate the time-varying variables
@chain main_info_df begin
    groupby(_,:project_id)
    transform!(_,
    [:status,:start_time,:end_time,:creator_id,
    :avg_price,:category,:price_quantity,:goal].=>x->fill_missing(x;method=:ffill),
    [:pledged,:backer_num,:update_num,
    :attention,:comment_num].=>interpolate_missing_linear;
    renamecols=false)
    select!(_,Not([:scraped_time]))
end
#+
# save the cleaned data
# save_object("$(project_dir)/data/prev_data/edited_data/main_info_df.jld2",main_info_df)