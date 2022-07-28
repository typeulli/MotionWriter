def onTick(image, dataset, tick, data, funcs, time_info):
    if dataset.start_time == tick:
        start, end, sep, hold, run = time_info
        dataset.x += ( data["position"][0] - dataset.x ) * (end - tick) / sep * hold / run
        dataset.y += ( data["position"][1] - dataset.y ) * (end - tick) / sep * hold / run
    return image