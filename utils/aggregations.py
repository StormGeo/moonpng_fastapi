from fastapi import HTTPException

def apply(dataset, params):
    if params.aggregation == "mean":
        return dataset.mean(dim="time")
    elif params.aggregation == "sum":
        return dataset.sum(dim="time")
    elif params.aggregation == "max":
        return dataset.max(dim="time")
    elif params.aggregation == "min":
        return dataset.min(dim="time")
    elif params.aggregation == "median":
        return dataset.median(dim="time")
    elif params.aggregation == "std":
        return dataset.std(dim="time")
    elif params.aggregation == "var":
        return dataset.var(dim="time")
    elif params.aggregation == "count":
        return dataset.count(dim="time")
    elif params.aggregation == "first": 
        return dataset.isel(time=0)
    elif params.aggregation == "last":  
        return dataset.isel(time=-1)
    else:
        raise HTTPException(status_code=400, detail="Aggregation method not supported")