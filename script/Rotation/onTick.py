def onTick(image, dataset, tick, data, funcs):
    dataset.x, dataset.y = funcs["math.__rotated"]((dataset.x, dataset.y), data["center"], data["angle"])
    return funcs["image.rotate"](image, data["center"], data["angle"])