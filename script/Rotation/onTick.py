def onTick(image, start_tick, end_tick, tick, funcs, data):
    return funcs["image.rotate"](image, data["angle"], data["center"])