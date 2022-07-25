def onTick(image, dataset, tick, data, funcs):
    if dataset.start_time == tick: dataset.x, dataset.y = data["position"]
    return image