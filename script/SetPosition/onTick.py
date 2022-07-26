def onTick(image, dataset, tick, data, funcs, time_info):
    if dataset.start_time == tick: dataset.x, dataset.y = data["position"]
    return image