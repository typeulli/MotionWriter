def onTick(image, dataset, tick, data, funcs, time_info):
    start, end, sep, hold, run = time_info
    if tick == start:
        dataset.affine = (
            funcs["math.sin"](data["angle"] * funcs["math.pi"] / 180) * data["speed"],
            funcs["math.cos"](data["angle"] * funcs["math.pi"] / 180) * data["speed"]
        )
    print("AFFINE!", data["angle"], funcs["math.sin"](data["angle"]), funcs["math.cos"](data["angle"]), dataset.affine)
    dataset.x += dataset.affine[0]
    dataset.y -= dataset.affine[1]
    return image