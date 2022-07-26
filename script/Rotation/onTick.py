def onTick(image, dataset, tick, data, funcs, time_info):
    dataset.x, dataset.y = funcs["math.__rotated"]((dataset.x, dataset.y), data["center"], data["angle"])
    start, end, sep, run = time_info
    return funcs["image.rotate"](image, data["center"], data["angle"])