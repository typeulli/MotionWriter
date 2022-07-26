def onTick(image, dataset, tick, data, funcs, time_info):
    return funcs["image.imread"](data["file"])