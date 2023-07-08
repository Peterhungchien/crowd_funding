function _convert_with_missing(T::Type,x)
    return ismissing(x) ? x : convert(T,x)
end


function _pad_forward(vec::AbstractVector)
    new_vec = copy(vec)
    first_nonmissing = findfirst(!ismissing,new_vec)
    isnothing(first_nonmissing) && return ArgumentError("The vector contains only missing values.")
    for ind in eachindex(new_vec)
        if ind < first_nonmissing
            continue
        else
            if ismissing(new_vec[ind])
                new_vec[ind] = new_vec[prevind(new_vec,ind)]
            end
        end
    end
    return new_vec
end

function _pad_backwards(vec::AbstractVector)
    return reverse(_pad_forward(reverse(vec)))
end





"""
Convert a string containing "yyyy-mm-dd HH:MM:SS" to a DateTime object.
An error occurs if this pattern is not found.
"""
function parse_datetime(s::AbstractString)
    dt_pattern = r"\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}"
    return DateTime(match(dt_pattern, s).match,"yyyy-mm-dd HH:MM:SS")
end


"""
Given a DateTime object that has implicit time zone "US/Pacific",
convert it to a DateTime object with implicit time zone "Asis/Shanghai".
"""
function convert_time_zone(t::DateTime)
	zoned_t=ZonedDateTime(t,TimeZone("US/Pacific",TimeZones.Class(:LEGACY)))
	return astimezone(zoned_t,tz"Asia/Shanghai") |> DateTime
end

"""
Take a string representation of the prices and quantities of goods of a crowdfunding project,
return a vector of tuples.
"""
function parse_price_quantity_string(s::AbstractString)::Vector{Tuple{Float64,Int64}}
    number_regex = r"(\d|\.)+"
    matches = eachmatch(number_regex,s) |> collect
    return [(parse(Float64,matches[i].match),parse(Int64,matches[i+1].match)) for i in 1:2:length(matches)]
end

"""
Given a vector containing prices and quantities of goods,
return the average price of the goods.
If the number of goods is greater than 2, the highest and lowest prices are removed.
"""
function compute_avg_price(vec::Vector{Tuple{Float64,Int64}})
    # get the price vector
    price_vec = getindex.(vec,1)
    if length(price_vec) <= 2
        return mean(price_vec)
    else
        # remove the highest and lowest price
        price_vec = sort(price_vec)[2:end-1]
        return mean(price_vec)
    end
end

"""
Compute the difference between each element in time_vec and the reference time
in unit of `unit`. The result is rounded up to the nearest integer.
"""
function compute_time_index(time_vec::AbstractVector{DateTime},refernce_time::DateTime;
    unit::TimePeriod)
    return ceil.(Int64,(time_vec.-refernce_time)./unit)
end


"""
    complete(df::AbstractDataFrame,index_col::Symbol)

Given an AbstractDataFrame containing time series data with
a discrete time index, use `missing` to fill observations whose index is between the
minium index and the maxium.
"""
function complete(df::AbstractDataFrame,index_col::Symbol)
    complete_index = minimum(df[:,index_col]):maximum(df[:,index_col]) |> collect
    complete_df = DataFrame(index_col=>complete_index)
    return sort(outerjoin(df,complete_df;on=index_col),index_col)
end

function complete(gdf::GroupedDataFrame,index_col::Symbol)
    # get the group keys, for we need to fill these values
    # to let this function work with combine
    group_keys = gdf.cols
    return combine(gdf) do sub_df
            sub_df = complete(sub_df,index_col)
            for group_key in group_keys
                sub_df[!,group_key] .= coalesce(sub_df[:,group_key]...)
            end
            sub_df
        end
end




"""
    interpolate_missing_linear(vec::AbstractVector{<:Union{Missing,Real}})

Interpolate missing values in a vector using linear interpolation.

# Arguments
- `vec::AbstractVector{<:Union{Missing,Real}}`: A vector containing missing values.

# Returns
- The input vector with missing values replaced by linearly interpolated values of
type Float64.
"""
function interpolate_missing_linear(vec::AbstractVector{<:Union{Missing,Real}})
    # find the index of missing values
    missing_index = findall(ismissing,vec)
    # find the index of non-missing values
    non_missing_index = findall(!ismissing,vec)
    # create a 1D linear interpolation object
    interp = LinearInterpolation(non_missing_index,vec[non_missing_index])
    # interpolate the missing values
    vec[missing_index] = convert.(Float64,interp.(missing_index))
    return vec
end

"""
    fill_missing(vec::AbstractVector; method=:ffill)

Fill in missing values in a vector using either forward or backward filling.

Arguments:
- vec: AbstractVector - the vector to fill in missing values for.
- method=:ffill - the filling method to use.
Can be either :ffill for forward filling or :bfill for backward filling.
"""
function fill_missing(vec::AbstractVector;method=:ffill)
    if method == :ffill
        return _pad_forward(vec)
    elseif method == :bfill
        return _pad_backwards(vec)
    else
        return ArgumentError("The method argument must be either :ffill or :bfill.")
    end
end

function nest(gdf::DataFrames.GroupedDataFrame)
    return combine(gdf,Not(groupcols(gdf)).=> Ref ∘ collect;renamecols=false)
end