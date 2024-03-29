def onTick(image, dataset, tick, data, funcs, time_info):
    cx, cy = data["center"]
    dataset.x, dataset.y = funcs["math.__rotated"]((dataset.x, dataset.y), (dataset.x if cx == -1 else cx , dataset.y if cy == -1 else cy), data["angle"])
    height, width, *_ = image.shape
    start, end, sep, hold, run = time_info
    #width//2, height//2
    return funcs["image.rotate"](image, data["center"], data["angle"]*run)