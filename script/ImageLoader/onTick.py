def onTick(image, dataset, tick, data, funcs):
    return funcs["image.imread"](data["file"])