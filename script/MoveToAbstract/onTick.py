def onTick(image, dataset, tick, data, funcs, time_info):
    start, end, sep, hold, run = time_info
    if tick == start:
        dataset.by_move = (
            ( data["position"][0] - dataset.x ) / ( (end - start) / sep * hold ) * run,
            ( data["position"][1] - dataset.y ) / ( (end - start) / sep * hold ) * run
        )
    print("MOVE!", tick, 1 / ( (end - start) / sep * hold ) * run)
    dataset.x += dataset.by_move[0]
    dataset.y += dataset.by_move[1]
    return image