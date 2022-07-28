def onTick(image, dataset, tick, data, funcs, time_info):
    dataset.x, dataset.y = funcs["math.__rotated"]((dataset.x, dataset.y), data["center"], data["angle"])
    height, width, *_ = image.shape
    start, end, sep, hold, run = time_info
    #width//2, height//2
    return funcs["image.rotate"](image, data["center"], data["angle"]*run)