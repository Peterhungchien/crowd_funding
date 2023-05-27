module Crowdfunding
    using DataFrames
    using Dates, TimeZones
    using StatsBase
    using Interpolations
    export parse_datetime, convert_time_zone, compute_time_index
    export parse_price_quantity_string, compute_avg_price
    export complete, interpolate_missing_linear, fill_missing

    include("preprocess.jl")
end