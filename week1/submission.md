# Do your counts match ours?
Yes

# What field types and analyzers did you use for the following fields and why?
For "name", "shortDescription" and "longDescription" I used English analyzer, along with a "keyword" multi-field.
For "regularPrice" I was searching for a numeric value that would fit for monetary transactions and has a high precision.
This lead me to this docs page: https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html#_which_type_should_i_use
The quick, mindless keyword scan of my brain noticed "trade accuracy" next to "scaled_float" data type and thought "bingo!".
Much later, after having indexed the full dataset, which took 18 minutes on my work laptop, did I notice that "trade" in that phrase was a verb and not a noun.
At the end, I got a storage optimized version of the price, albeit should not be used for transactions. I guess it works for the search purposes.

# Compare your Field mappings with the instructors.  Where did you align and where did you differ?  What are the pros and cons to the different approaches?
At the time of my submission they weren't shared yet.

# Were you able to get the “ipad 2” to show up in the top of your results?  How many iterations did it take for you to get there, if at all? (we’re not scoring this, of course, it’s just worth noting that hand tuning like this can often be quite time consuming.)
Yes. It took some to time to understand the syntax, however following the instructions finally lead to the outcome.
However it's far from perfect. I believe it works OK for using brand names as a part of a search query like "Nokia", "Walkman", etc. but stutters when dealing with queries like "camera" or "calculator".
Having two or more words combined decreases the quality.
